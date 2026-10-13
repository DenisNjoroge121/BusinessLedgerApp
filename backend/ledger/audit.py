from django.conf import settings

from .models import AuditLog


def log_entry_action(request, verb, entry):
    user = request.user
    label = entry.get_entry_type_display()
    action = f"{verb} {label} of KSh {entry.amount:,.2f} for {entry.customer.name}"
    AuditLog.objects.create(
        business_id=user.business_id,
        user=user,
        action=action[:255],
        ledger_entry=entry,
        # Behind a proxy in production, REMOTE_ADDR is the proxy's address.
        # We'll fix that in the deployment phase.
        ip_address=request.META.get("REMOTE_ADDR") or None,
        device_info=request.META.get("HTTP_USER_AGENT", "")[:255],
        device_id=request.META.get("HTTP_X_DEVICE_ID", "")[:100],
        is_flagged=entry.amount >= settings.LARGE_TRANSACTION_THRESHOLD,
    )