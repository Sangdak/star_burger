from rest_framework import serializers

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            'product',
            'quantity',
        ]


class OrderSerializer(serializers.ModelSerializer):
    products = OrderItemSerializer(many=True, allow_empty=False, write_only=True)

    class Meta:
        model = Order
        fields = '__all__'
        # fields = ['id', 'firstname', 'lastname', 'phonenumber', 'address', 'products']
        # extra_kwargs = {'products': {'write_only': True}}
