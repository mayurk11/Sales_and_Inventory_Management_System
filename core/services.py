from django.db import transaction
from .models import Inventory
from rest_framework.exceptions import ValidationError

@transaction.atomic
def confirm_order(order):

    if order.status != 'DRAFT':
        raise ValidationError("Order must be in DRAFT to confirm")

    insufficient_products = []

    # Lock rows to avoid race condition
    for item in order.items.all():
        inventory = Inventory.objects.select_for_update().get(product=item.product)

        if item.quantity > inventory.quantity:
            insufficient_products.append({
                "product": item.product.name,
                "available": inventory.quantity,
                "requested": item.quantity
            })

    if insufficient_products:
        raise ValidationError({
            "error": "Insufficient stock",
            "details": insufficient_products
            })

    # Deduct stock
    for item in order.items.all():
        inventory = Inventory.objects.get(product=item.product)
        inventory.quantity -= item.quantity
        inventory.save()

    order.status = 'CONFIRMED'
    order.save()
    
    
def deliver_order(order):

    if order.status != 'CONFIRMED':
        raise ValidationError("Only confirmed orders can be delivered")

    order.status = 'DELIVERED'
    order.save()