from decimal import Decimal

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from accounts.models import User

from . import services
from .models import (AuditLog, BusinessCategory, CerealItemType, Customer, LedgerEntry)


def _user(serializer):
    return serializer.context["request"].user


class CerealItemTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CerealItemType
        fields = ["id", "category", "name", "default_price_per_kg"]

    def validate_category(self, value):
        if value.business_id != _user(self).business_id:
            raise serializers.ValidationError("Category not found.")
        return value


class CategorySerializer(serializers.ModelSerializer):
    cereal_types = CerealItemTypeSerializer(many=True, read_only=True)

    class Meta:
        model = BusinessCategory
        fields = ["id", "name", "category_type", "icon", "sort_order",
                  "cereal_types"]


class CustomerSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Customer
        fields = ["id", "category", "category_name", "name", "phone",
                  "credit_limit", "current_balance", "last_activity_date",
                  "created_at"]
        read_only_fields = ["current_balance", "last_activity_date", "created_at"]

    def validate_category(self, value):
        if value.business_id != _user(self).business_id:
            raise serializers.ValidationError("Category not found.")
        return value

    def validate(self, attrs):
        if "credit_limit" in attrs and _user(self).role != User.Role.OWNER:
            raise serializers.ValidationError(
                {"credit_limit": "Only the owner can set credit limits."}
            )
        if (
            self.instance
            and "category" in attrs
            and attrs["category"].pk != self.instance.category_id
        ):
            raise serializers.ValidationError(
                {"category": "A customer cannot be moved to another category."}
            )
        return attrs


class LedgerEntrySerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(
        source="created_by.username", read_only=True, default=""
    )

    class Meta:
        model = LedgerEntry
        fields = ["id", "client_uuid", "customer", "parent_entry", "entry_type",
                  "date", "cereal_type", "item_description", "quantity_kg",
                  "price_per_kg", "payment_method", "note", "amount",
                  "running_balance", "created_by_name", "created_at"]
        read_only_fields = fields


class EntryCreateSerializer(serializers.Serializer):
    client_uuid = serializers.UUIDField(required=False)
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())
    entry_type = serializers.ChoiceField(choices=LedgerEntry.EntryType.choices)
    date = serializers.DateField(required=False)
    amount = serializers.DecimalField(
        max_digits=12, decimal_places=2, min_value=Decimal("0.01"), required=False
    )
    parent_entry = serializers.PrimaryKeyRelatedField(
        queryset=LedgerEntry.objects.filter(is_deleted=False),
        required=False, allow_null=True,
    )
    cereal_type = serializers.PrimaryKeyRelatedField(
        queryset=CerealItemType.objects.all(), required=False, allow_null=True
    )
    item_description = serializers.CharField(
        max_length=255, required=False, allow_blank=True, default=""
    )
    quantity_kg = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=Decimal("0.01"), required=False
    )
    price_per_kg = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=Decimal("0.00"), required=False
    )
    payment_method = serializers.ChoiceField(
        choices=LedgerEntry.Method.choices, required=False,
        allow_blank=True, default="",
    )
    note = serializers.CharField(
        max_length=255, required=False, allow_blank=True, default=""
    )

    def validate_customer(self, value):
        if value.category.business_id != _user(self).business_id:
            raise serializers.ValidationError("Customer not found.")
        return value

    def validate_parent_entry(self, value):
        if value is not None and (
            value.customer.category.business_id != _user(self).business_id
        ):
            raise serializers.ValidationError("Entry not found.")
        return value

    def validate_cereal_type(self, value):
        if value is not None and value.category.business_id != _user(self).business_id:
            raise serializers.ValidationError("Cereal type not found.")
        return value

    def validate_client_uuid(self, value):
        existing = (
            LedgerEntry.objects.filter(client_uuid=value)
            .select_related("customer__category")
            .first()
        )
        if existing and existing.customer.category.business_id != _user(self).business_id:
            raise serializers.ValidationError("Invalid client_uuid.")
        return value

    def create(self, validated_data):
        try:
            return services.add_entry(created_by=_user(self), **validated_data)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"detail": exc.messages})


class AuditLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True, default="")
    role = serializers.CharField(source="user.role", read_only=True, default="")

    class Meta:
        model = AuditLog
        fields = ["id", "username", "role", "action", "ledger_entry",
                  "ip_address", "device_info", "device_id", "is_flagged",
                  "timestamp"]
        read_only_fields = fields