import uuid
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class BusinessCategory(models.Model):
    class CategoryType(models.TextChoices):
        ONION = "ONION", "Onions"
        CEREAL = "CEREAL", "Cereals"
        CUSTOM = "CUSTOM", "General / Custom"

    business = models.ForeignKey(
        "accounts.Business", on_delete=models.CASCADE, related_name="categories"
    )
    name = models.CharField(max_length=100)
    category_type = models.CharField(
        max_length=10, choices=CategoryType.choices, default=CategoryType.CUSTOM
    )
    icon = models.CharField(max_length=10, default="📦")
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name_plural = "business categories"

    def __str__(self):
        return f"{self.name} ({self.category_type})"


class CerealItemType(models.Model):
    category = models.ForeignKey(
        BusinessCategory, on_delete=models.CASCADE, related_name="cereal_types"
    )
    name = models.CharField(max_length=100)  # Maize, Beans, Green Grams...
    default_price_per_kg = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Customer(models.Model):
    category = models.ForeignKey(
        BusinessCategory, on_delete=models.CASCADE, related_name="customers"
    )
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True)
    credit_limit = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("50000.00")
    )
    # Maintained ONLY by ledger.services. Never edit directly.
    current_balance = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00")
    )
    last_activity_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} - Bal: KSh {self.current_balance}"


class LedgerEntry(models.Model):
    class EntryType(models.TextChoices):
        DEBT = "DEBT", "Debt / Goods Taken"
        PAYMENT = "PAYMENT", "Payment Made"
        DISCOUNT = "DISCOUNT", "Discount Given"

    class Method(models.TextChoices):
        CASH = "CASH", "Cash"
        MPESA = "MPESA", "M-Pesa"
        BANK = "BANK", "Bank"
        OTHER = "OTHER", "Other"

    # Generated on the phone so offline entries can sync without duplicates.
    client_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="ledger_entries"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    parent_entry = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True,
        related_name="sub_entries",
    )
    entry_type = models.CharField(max_length=10, choices=EntryType.choices)
    date = models.DateField()

    # Debt-specific fields
    cereal_type = models.ForeignKey(
        CerealItemType, on_delete=models.SET_NULL, null=True, blank=True
    )
    item_description = models.CharField(max_length=255, blank=True)
    quantity_kg = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    price_per_kg = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )

    # Payment-specific
    payment_method = models.CharField(
        max_length=10, choices=Method.choices, blank=True
    )
    note = models.CharField(max_length=255, blank=True)

    amount = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    # Maintained ONLY by ledger.services.
    running_balance = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00")
    )

    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["date", "created_at", "id"]
        indexes = [models.Index(fields=["customer", "date"])]

    def __str__(self):
        return f"{self.entry_type} KSh {self.amount} ({self.customer.name})"

class AuditLog(models.Model):
    business = models.ForeignKey(
        "accounts.Business", on_delete=models.CASCADE, related_name="audit_logs"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    action = models.CharField(max_length=255)
    ledger_entry = models.ForeignKey(
        LedgerEntry, on_delete=models.SET_NULL, null=True, blank=True
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    device_info = models.CharField(max_length=255, blank=True)  # User-Agent
    device_id = models.CharField(max_length=100, blank=True)    # sent by the app
    is_flagged = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp", "-id"]

    def __str__(self):
        return f"{self.timestamp:%Y-%m-%d %H:%M} {self.action}"