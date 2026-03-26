from rest_framework import serializers
from .models import *

from rest_framework.exceptions import ValidationError

from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Dealer

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class DealerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dealer
        fields = '__all__'


class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = '__all__'
        

class OrderItemSerializer(serializers.ModelSerializer):
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    line_total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'unit_price', 'line_total']
        
        
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['dealer', 'order_number', 'total_amount', 'status']

    def create(self, validated_data):
        items_data = validated_data.pop('items')

        user = self.context['request'].user
        dealer = user.dealer   # ✅ auto assign

        order = Order.objects.create(dealer=dealer)

        for item_data in items_data:
            product = item_data['product']

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item_data['quantity'],
                unit_price=product.price
            )

        order.update_total()
        return order
    
    def update(self, instance, validated_data):

        if instance.status != 'DRAFT':
            raise ValidationError("Only draft orders can be edited")

        return super().update(instance, validated_data)
    
class DealerRegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Dealer
        fields = ['username', 'password', 'name', 'email', 'phone']

    def create(self, validated_data):
        username = validated_data.pop('username')
        password = validated_data.pop('password')

        # Create User
        user = User.objects.create_user(
            username=username,
            password=password
        )

        # Create Dealer
        dealer = Dealer.objects.create(
            user=user,
            **validated_data
        )

        return dealer