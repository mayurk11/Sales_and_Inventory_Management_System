from django.shortcuts import render


# Create your views here.
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from .models import Product, Dealer, Order, Inventory
from .serializers import (
    ProductSerializer,
    DealerSerializer,
    OrderSerializer,
    InventorySerializer
)
from .services import confirm_order, deliver_order

from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdminUserCustom, IsDealerUser

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import DealerRegisterSerializer

class DealerRegisterView(APIView):

    def post(self, request):
        serializer = DealerRegisterSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Dealer registered successfully"},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminUserCustom]  
    
    
class DealerViewSet(viewsets.ModelViewSet):
    queryset = Dealer.objects.all()
    serializer_class = DealerSerializer
    permission_classes = [IsAdminUserCustom]
    
class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    permission_classes = [IsAdminUserCustom]
    
    
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    
        
    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Order.objects.all()

        return Order.objects.filter(dealer__user=user)   
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        order = self.get_object()

        confirm_order(order, request.user)

        return Response({"message": "Order confirmed"})
                
        
    @action(detail=True, methods=['post'])
    def deliver(self, request, pk=None):
        order = self.get_object()

        try:
            deliver_order(order)
            return Response({"message": "Order delivered"})
        except ValueError as e:
            if isinstance(e.args[0], dict):
                return Response(e.args[0], status=400)
            return Response({"error": str(e)}, status=400)
        except Exception as e:
            return Response({"error": "Internal server error"}, status=500)
        
    def destroy(self, request, *args, **kwargs):
        order = self.get_object()

        # If order was confirmed → restore stock
        if order.status == 'CONFIRMED':
            for item in order.items.all():
                inventory = Inventory.objects.get(product=item.product)
                inventory.quantity += item.quantity
                inventory.save()

        order.delete()
        return Response({"message": "Order deleted successfully"})
    
    class OrderViewSet(viewsets.ModelViewSet):
        queryset = Order.objects.all()
        serializer_class = OrderSerializer

    def get_permissions(self):
        # Default → user must be logged in
        permissions = [IsAuthenticated()]

        if self.action == 'create':
            permissions.append(IsDealerUser())

        elif self.action == 'confirm':
            permissions.append(IsDealerUser())

        elif self.action == 'deliver':
            permissions.append(IsAdminUserCustom())  # 🔥 ONLY ADMIN

        return permissions
    
