from rest_framework.routers import DefaultRouter

from .views import (AuditLogViewSet, CategoryViewSet, CerealItemTypeViewSet, CustomerViewSet, EntryViewSet)

router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="category")
router.register("cereal-types", CerealItemTypeViewSet, basename="cereal-type")
router.register("customers", CustomerViewSet, basename="customer")
router.register("entries", EntryViewSet, basename="entry")
router.register("audit-logs", AuditLogViewSet, basename="audit-log")

urlpatterns = router.urls