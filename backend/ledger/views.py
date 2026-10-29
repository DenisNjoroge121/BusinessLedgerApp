from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import BusinessCategory, Customer, LedgerEntry
from .serializers import CategorySerializer, CustomerSerializer, LedgerEntrySerializer
from accounts.permissions import IsOwnerOrHelper, IsOwnerOnly
from .services import create_ledger_entry # The function we wrote in Phase 1

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Users only see categories they own or are assigned to
        return BusinessCategory.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class CustomerViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerSerializer
    permission_classes = [IsOwnerOrHelper]

    def get_queryset(self):
        # Filter customers based on the user's categories
        return Customer.objects.filter(category__owner=self.request.user)

class LedgerViewSet(viewsets.ModelViewSet):
    serializer_class = LedgerEntrySerializer
    permission_classes = [IsOwnerOrHelper]

    def get_queryset(self):
        return LedgerEntry.objects.filter(customer__category__owner=self.request.user)

    def create(self, request, *args, **kwargs):
        # 1. Validate the input data using the serializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 2. Extract data for the service layer
        data = serializer.validated_data
        customer_id = data['customer'].id
        
        try:
            # 3. CALL THE SERVICE LAYER (Atomic Lock happens here)
            entry = create_ledger_entry(
                customer_id=customer_id,
                user=request.user,
                entry_data=data
            )
            
            # 4. Return the created entry as JSON
            output_serializer = self.get_serializer(entry)
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
