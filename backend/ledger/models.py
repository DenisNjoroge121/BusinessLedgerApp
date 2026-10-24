from django.db import models
from django.conf import settings
from decimal import Decimal

class BusinessCategory(models.Model):
    class CategoryType(models.TextChoices):
        ONION = 'ONION', 'Onion Category'
        CEREAL = 'CEREAL', 'Cereal Category'
        CUSTOM = 'CUSTOM', 'General / Custom'

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100)
    category_type = models.CharField(max_length=10, choices=CategoryType.choices, default=CategoryType.CUSTOM)
    icon = models.CharField(max_length=10, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.category_type})"

class CerealItemType(models.Model):
    category = models.ForeignKey(BusinessCategory, on_delete=models.CASCADE, related_name='cereal_types')
    name = models.CharField(max_length=100) 
    default_price_per_kg = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        return self.name

class Customer(models.Model):
    category = models.ForeignKey(BusinessCategory, on_delete=models.CASCADE, related_name='customers')
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True, null=True)
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('50000.00'))
    current_balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    last_activity_date = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - Bal: {self.current_balance}"

class LedgerEntry(models.Model):
    class EntryType(models.TextChoices):
        DEBT = 'DEBT', 'Debt / Goods Taken '
        PAYMENT = 'PAYMENT', 'Payment Made '
        DISCOUNT = 'DISCOUNT', 'Discount Given '

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='ledger_entries')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    # Hierarchical linkage: allows a payment to be linked to a specific debt
    parent_entry = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='sub_entries')
    
    entry_type = models.CharField(max_length=10, choices=EntryType.choices)
    date = models.DateField()

    # Debt Specifics (Null for payments/discounts)
    cereal_type = models.ForeignKey(CerealItemType, on_delete=models.SET_NULL, null=True, blank=True)
    item_description = models.CharField(max_length=255, blank=True, null=True)
    quantity_kg = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    price_per_kg = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    # Financials
    amount = models.DecimalField(max_digits=12, decimal_places=2) 
    running_balance = models.DecimalField(max_digits=12, decimal_places=2) 
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'created_at']

class HelperAuditLog(models.Model):
    helper = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action = models.CharField(max_length=255) 
    ledger_entry = models.ForeignKey(LedgerEntry, on_delete=models.CASCADE, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_flagged = models.BooleanField(default=False)
