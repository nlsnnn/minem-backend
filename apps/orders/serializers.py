from rest_framework import serializers
from django.db import transaction

from .models import Order, OrderItem, OrderCustomer
from apps.main.models import ProductVariant


class OrderCustomerSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели информации о клиенте заказа
    """

    class Meta:
        model = OrderCustomer
        fields = [
            "id",
            "full_name",
            "email",
            "phone",
            "city",
            "shipping_address",
            "comment",
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели позиции заказа
    """

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product_variant",
            "quantity",
            "price",
        ]


class OrderSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели заказа
    """

    items = OrderItemSerializer(many=True, read_only=True)
    customer_info = OrderCustomerSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "status",
            "total_amount",
            "items",
            "customer_info",
            "created_at",
            "updated_at",
        ]


class OrderItemCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели позиции заказа
    """

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product_variant",
            "quantity",
        ]


class OrderCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания заказа
    """

    items = OrderItemCreateSerializer(many=True, write_only=True)
    customer_info = OrderCustomerSerializer(write_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "status",
            "items",
            "customer_info",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        customer_data = validated_data.pop("customer_info", {})

        with transaction.atomic():
            variants = ProductVariant.objects.select_for_update().filter(
                id__in=[item["product_variant"].id for item in items_data],
                is_active=True,
            )

            total_amount = 0
            for item in items_data:
                requested_variant: ProductVariant = item["product_variant"]
                requested_quantity = int(item.get("quantity", 1))

                variant = next(
                    (v for v in variants if v.id == requested_variant.id), None
                )

                if not variant:
                    raise serializers.ValidationError(
                        f"Вариант товара с ID {requested_variant.id} недоступен."
                    )

                if variant.stock < requested_quantity:
                    raise serializers.ValidationError(
                        f"Недостаточно товара для варианта с ID {requested_variant.id}."
                    )

                total_amount += variant.price * requested_quantity
                item["price"] = variant.price
                variant.stock -= requested_quantity
                variant.save()

            order = Order.objects.create(
                total_amount=total_amount, status="awaiting_payment"
            )

            OrderCustomer.objects.create(order=order, **customer_data)

            OrderItem.objects.bulk_create(
                [OrderItem(order=order, **item) for item in items_data]
            )

        return order
