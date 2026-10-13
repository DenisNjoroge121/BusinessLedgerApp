from django.contrib import admin

from .models import (AuditLog, BusinessCategory, CerealItemType, Customer, LedgerEntry)

admin.site.register(BusinessCategory)
admin.site.register(CerealItemType)
admin.site.register(Customer)
admin.site.register(LedgerEntry)
admin.site.register(AuditLog)