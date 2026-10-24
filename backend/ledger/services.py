# ledger/services.py
from django.db import transaction
from .models import Customer, LedgerEntry

def create_ledger_entry(customer_id, user, entry_data):
    with transaction.atomic():
        # 1. LOCK the customer row. No other request can touch this customer until this block finishes.
        customer = Customer.objects.select_for_update().get(pk=customer_id)
        
        # 2. Determine the value change
        # Debt increases balance (+), Payments decrease balance (-)
        amount = entry_data['amount']
        if entry_data['entry_type'] in ['PAYMENT', 'DISCOUNT']:
            change = -amount
        else:
            change = amount
        
        # 3. Calculate new running balance
        new_balance = customer.current_balance + change
        
        # 4. Create the entry
        entry = LedgerEntry.objects.create(
            customer=customer,
            created_by=user,
            amount=amount,
            running_balance=new_balance,
            **entry_data
        )
        
        # 5. Update the cached balance on the customer
        customer.current_balance = new_balance
        customer.save()
        
        return entry
