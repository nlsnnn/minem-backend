from rest_framework import serializers

from .models import Order, OrderItem, OrderCustomer
from .services import OrderCreationService


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
    Сериализатор для создания заказа с оплатой.
    """

    items = OrderItemCreateSerializer(many=True, write_only=True)
    customer_info = OrderCustomerSerializer(write_only=True)
    payment_url = serializers.CharField(read_only=True)
    return_url = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Order
        fields = [
            "id",
            "status",
            "items",
            "customer_info",
            "payment_url",
            "return_url",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "status", "created_at", "updated_at"]

    def create(self, validated_data):
        """
        Создает заказ с платежом через сервис.
        """
        items_data = validated_data.pop("items", [])
        if len(items_data) == 0:
            raise serializers.ValidationError(
                {"items": "Список товаров не может быть пустым."}
            )

        customer_data = validated_data.pop("customer_info", {})
        return_url = validated_data.pop("return_url", None)

        service = OrderCreationService()
        order = service.create_order_with_payment(
            items_data=items_data,
            customer_data=customer_data,
            return_url=return_url,
        )

        return order
