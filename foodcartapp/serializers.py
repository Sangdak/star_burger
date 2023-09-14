from django.db import transaction
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

    def create(self, validated_data):
        products_items = validated_data.pop('products')
        for item in products_items:
            item['price'] = item['product'].price
        with transaction.atomic():
            order = Order.objects.create(**validated_data)
            order_items = [OrderItem(order=order, **item) for item in products_items]
            OrderItem.objects.bulk_create(order_items)

            return order

    class Meta:
        model = Order
        fields = [
            'id',
            'firstname',
            'lastname',
            'phonenumber',
            'address',
            'products',
        ]
