from django.contrib import admin
from .models import BusinessCategory, CerealItemType, Customer, LedgerEntry, HelperAuditLog

@admin.register(BusinessCategory)
class BusinessCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category_type', 'owner', 'created_at')
    list_filter = ('category_type', 'owner')
    search_fields = ('name',)

@admin.register(CerealItemType)
class CerealItemTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'default_price_per_kg')
    list_filter = ('category',)
    search_fields = ('name',)

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'current_balance', 'phone', 'last_activity_date')
    list_filter = ('category',)
    search_fields = ('name', 'phone')
    # Make current_balance read-only in admin to force use of LedgerEntries
    readonly_fields = ('current_balance',) 

@admin.register(LedgerEntry)
class LedgerEntryAdmin(admin.ModelAdmin):
    list_display = ('customer', 'entry_type', 'amount', 'running_balance', 'date', 'created_by')
    list_filter = ('entry_type', 'date', 'customer__category')
    search_fields = ('customer__name', 'item_description')
    date_hierarchy = 'date' # Adds a nice date-based drill-down at the top
    
    # Ensure the running_balance cannot be edited manually in Admin
    readonly_fields = ('running_balance',)

@admin.register(HelperAuditLog)
class HelperAuditLogAdmin(admin.ModelAdmin):
    list_display = ('helper', 'action', 'timestamp', 'is_flagged')
    list_filter = ('is_flagged', 'timestamp')
    # Audit logs should NEVER be editable
    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]
