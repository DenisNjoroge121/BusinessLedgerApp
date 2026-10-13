from decimal import Decimal, ROUND_HALF_UP

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from .models import Customer, LedgerEntry

CENT = Decimal("0.01")
ZERO = Decimal("0.00")


def _money(value):
    return Decimal(value).quantize(CENT, rounding=ROUND_HALF_UP)


@transaction.atomic
def recalculate_customer(customer_id):
    """Rebuild every running balance for one customer, in date order."""
    # fetches the customer record while applying a SELECT... FOR UPDATE
    customer = Customer.objects.select_for_update().get(pk=customer_id) 
    #queries all valid ledger records belonging to this customer
    entries = customer.ledger_entries.filter(is_deleted=False).order_by(
        "date", "created_at", "id"
    )
    balance = ZERO
    changed = []
    #loops through the pulled ledger entry
    for entry in entries:
        if entry.entry_type == LedgerEntry.EntryType.DEBT:
            balance += entry.amount
        else:
            balance -= entry.amount

        #compares the newly computed balance against the currently written on database object row
        if entry.running_balance != balance:
            entry.running_balance = balance
            changed.append(entry)

    #checks if any entries modified. if yes, execute a single efficient SQL update statement
    if changed:
        LedgerEntry.objects.bulk_update(changed, ["running_balance"])
    customer.current_balance = balance
    customer.last_activity_date = timezone.now()
    #commits only the two database fields back to the locked database records &returns the final computed balance value
    customer.save(update_fields=["current_balance", "last_activity_date"])
    return balance


@transaction.atomic
def add_entry(
    *, customer, created_by, entry_type, date=None, amount=None,
    parent_entry=None, cereal_type=None, item_description="",
    quantity_kg=None, price_per_kg=None,
    payment_method="", note="", client_uuid=None,
):
    # Idempotent: the same entry sent twice (offline sync retry) is saved once.
    if client_uuid:
        existing = LedgerEntry.objects.filter(client_uuid=client_uuid).first()
        if existing:
            return existing
    #validate the system input parameter against allowed configuration types definedin model layers
    if entry_type not in LedgerEntry.EntryType.values:
        raise ValidationError("Unknown entry type.")

    customer = Customer.objects.select_for_update().get(pk=customer.pk)

    if entry_type == LedgerEntry.EntryType.DEBT:
        #rejects transaction if application attempts to nest a primary DEBT record under an existing ledger entry
        if parent_entry is not None:
            raise ValidationError("A debt cannot be nested under another entry.")
        #Structural safety checks ensuring the assigned stock item inventory structure aligns natively with the operational category assigned to the targeted customer profile.
        if cereal_type is not None:
            if cereal_type.category_id != customer.category_id:
                raise ValidationError(
                    "That cereal type belongs to a different category."
                )
            if price_per_kg is None:
                price_per_kg = cereal_type.default_price_per_kg
        if quantity_kg is not None and price_per_kg is not None:
            amount = _money(Decimal(quantity_kg) * Decimal(price_per_kg))

    if amount is None:
        raise ValidationError("Amount is required.")
    amount = _money(amount)
    if amount <= 0:
        #Re-normalizes the raw tracking amount to protect against formatting variation and enforces that all entries have a positive, non-zero value.
        raise ValidationError("Amount must be greater than zero.")

    if parent_entry is not None:
        parent = LedgerEntry.objects.select_for_update().get(pk=parent_entry.pk)
        # Verifies that the parent record belongs to the exact same customer, is classified as a valid DEBT line item type, and has not been soft-deleted.
        if (
            parent.customer_id != customer.pk
            or parent.entry_type != LedgerEntry.EntryType.DEBT
            or parent.is_deleted
        ):
            raise ValidationError("Invalid parent debt.")
        #Queries all existing valid sub-entries nested under the parent record, sums their amount fields directly inside the database engine via SQL aggregation, and falls back to 0.00 if no sub-entries exist yet
        used = (
            parent.sub_entries.filter(is_deleted=False).aggregate(t=Sum("amount"))["t"]
            or ZERO
        )
        #Enforces a financial limit ceiling by ensuring the sum of existing child entries plus the new entry does not exceed the total value allocated to the primary parent transaction.
        if used + amount > parent.amount:
            raise ValidationError(
                f"Only KSh {parent.amount - used} is left on this debt."
            )
        
    #Sets up an optional keyword argument dictionary containing the unique synchronization identifier client_uuid, if provided.
    kwargs = {}
    if client_uuid:
        kwargs["client_uuid"] = client_uuid

    entry = LedgerEntry.objects.create(
        customer=customer,
        created_by=created_by,
        parent_entry=parent_entry,
        entry_type=entry_type,
        date=date or timezone.localdate(),
        cereal_type=cereal_type,
        item_description=item_description,
        quantity_kg=Decimal(quantity_kg) if quantity_kg is not None else ZERO,
        price_per_kg=Decimal(price_per_kg) if price_per_kg is not None else ZERO,
        payment_method=(
            payment_method or LedgerEntry.Method.CASH
            if entry_type == LedgerEntry.EntryType.PAYMENT
            else ""
        ),
        note=note,
        amount=amount,
        **kwargs,
    )
    recalculate_customer(customer.pk)
    entry.refresh_from_db()
    return entry

# Wraps the record deletion routing inside an isolated database transaction block.
@transaction.atomic
def delete_entry(entry):
    """Soft-delete an entry (and, for a debt, everything nested under it)."""
    entry = LedgerEntry.objects.select_for_update().get(pk=entry.pk)
    entry.is_deleted = True
    entry.save(update_fields=["is_deleted", "updated_at"])
    if entry.entry_type == LedgerEntry.EntryType.DEBT:
        entry.sub_entries.update(is_deleted=True)
    recalculate_customer(entry.customer_id)