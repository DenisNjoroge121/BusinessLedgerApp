from rest_framework import mixins, status, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from . import services
from .audit import log_entry_action
from .models import AuditLog, BusinessCategory, CerealItemType, Customer, LedgerEntry
from .permissions import IsOwner, OwnerWritesMemberReads, StaffWritesViewerReads
from .serializers import (AuditLogSerializer, CategorySerializer, CerealItemTypeSerializer, CustomerSerializer, EntryCreateSerializer, LedgerEntrySerializer)


class NoDeleteViewSet(
    mixins.CreateModelMixin, mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet,
):
    """Create / read / update / list. Deliberately no delete."""


class CategoryViewSet(NoDeleteViewSet):
    serializer_class = CategorySerializer
    permission_classes = [OwnerWritesMemberReads]

    def get_queryset(self):
        return BusinessCategory.objects.filter(
            business_id=self.request.user.business_id
        ).prefetch_related("cereal_types")

    def perform_create(self, serializer):
        serializer.save(business_id=self.request.user.business_id)


class CerealItemTypeViewSet(NoDeleteViewSet):
    serializer_class = CerealItemTypeSerializer
    permission_classes = [OwnerWritesMemberReads]

    def get_queryset(self):
        qs = CerealItemType.objects.filter(
            category__business_id=self.request.user.business_id
        )
        category = self.request.query_params.get("category")
        if category and category.isdigit():
            qs = qs.filter(category_id=category)
        return qs


class CustomerViewSet(NoDeleteViewSet):
    serializer_class = CustomerSerializer
    permission_classes = [StaffWritesViewerReads]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name", "phone"]
    ordering_fields = ["name", "current_balance", "last_activity_date"]

    def get_queryset(self):
        qs = Customer.objects.filter(
            category__business_id=self.request.user.business_id
        ).select_related("category")
        category = self.request.query_params.get("category")
        if category and category.isdigit():
            qs = qs.filter(category_id=category)
        return qs


class EntryViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin, viewsets.GenericViewSet,
):
    serializer_class = LedgerEntrySerializer
    permission_classes = [StaffWritesViewerReads]

    def get_queryset(self):
        qs = LedgerEntry.objects.filter(
            customer__category__business_id=self.request.user.business_id,
            is_deleted=False,
        ).select_related("created_by", "customer")
        customer = self.request.query_params.get("customer")
        if customer and customer.isdigit():
            qs = qs.filter(customer_id=customer)
        return qs

    def create(self, request, *args, **kwargs):
        serializer = EntryCreateSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        uid = serializer.validated_data.get("client_uuid")
        is_retry = bool(uid) and LedgerEntry.objects.filter(client_uuid=uid).exists()
        entry = serializer.save()
        if not is_retry:  # an offline-sync retry must not be logged twice
            log_entry_action(request, "Added", entry)
        return Response(
            LedgerEntrySerializer(entry, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    def perform_destroy(self, instance):
        services.delete_entry(instance)
        log_entry_action(self.request, "Deleted", instance)


class AuditPagination(PageNumberPagination):
    page_size = 50


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AuditLogSerializer
    permission_classes = [IsOwner]
    pagination_class = AuditPagination

    def get_queryset(self):
        qs = AuditLog.objects.filter(
            business_id=self.request.user.business_id
        ).select_related("user")
        if self.request.query_params.get("flagged") == "true":
            qs = qs.filter(is_flagged=True)
        return qs