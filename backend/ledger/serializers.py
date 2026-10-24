from rest_framework import serializers
from .models import BusinessCategory, CerealItemType, Customer, LedgerEntry

class CerealItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CerealItemType
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    cereal_types = CerealItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = BusinessCategory
        fields = '__all__'

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class LedgerEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = LedgerEntry
        fields = '__all__'
        read_only_fields = ['running_balance', 'created_by']
