from rest_framework import serializers
from .models import *

from rest_framework.exceptions import ValidationError



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
    class Meta:
        model = OrderItem
        fields = '__all__'
        read_only_fields = ['line_total', 'order']
        
        
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['order_number', 'total_amount', 'status']

    def create(self, validated_data):
        items_data = validated_data.pop('items')

        request = self.context.get('request')
        user = request.user

        # Get dealer linked to logged-in user
        dealer = user.dealer

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