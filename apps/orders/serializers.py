import re
from rest_framework import serializers
from django.core.validators import MinValueValidator, MaxValueValidator, EmailValidator
from django.utils.html import escape

from .models import Order, OrderItem, OrderCustomer
from .service import OrderCreationService


class OrderCustomerSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели информации о клиенте заказа
    """

    full_name = serializers.CharField(
        max_length=100,
        required=True,
        error_messages={
            "required": "Имя обязательно для заполнения",
            "max_length": "Имя не должно превышать 100 символов",
        },
    )
    email = serializers.EmailField(
        required=True,
        validators=[EmailValidator(message="Введите корректный email адрес")],
    )
    phone = serializers.CharField(
        max_length=20,
        required=True,
        error_messages={"required": "Телефон обязателен для заполнения"},
    )

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

    def validate_phone(self, value):
        """Валидация номера телефона"""
        # Убираем все символы кроме цифр и +
        cleaned = re.sub(r"[^\d+]", "", value)
        if len(cleaned) < 10:
            raise serializers.ValidationError(
                "Номер телефона должен содержать минимум 10 цифр"
            )
        return cleaned

    def validate_full_name(self, value):
        """Защита от XSS в имени"""
        return escape(value.strip())

    def validate_comment(self, value):
        """Защита от XSS в комментариях"""
        if value:
            return escape(value.strip())
        return value


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

    quantity = serializers.IntegerField(
        validators=[
            MinValueValidator(1, message="Минимальное количество: 1"),
            MaxValueValidator(100, message="Максимальное количество за раз: 100"),
        ],
        error_messages={
            "required": "Количество обязательно",
            "invalid": "Количество должно быть целым числом",
        },
    )

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

    def validate_items(self, value):
        """Валидация списка товаров"""
        if not value:
            raise serializers.ValidationError("Список товаров не может быть пустым")
        if len(value) > 50:
            raise serializers.ValidationError("Максимум 50 товаров в одном заказе")

        variant_ids = [item["product_variant"].id for item in value]
        if len(variant_ids) != len(set(variant_ids)):
            raise serializers.ValidationError(
                "В заказе не должно быть дублирующихся товаров"
            )

        return value

    def create(self, validated_data):
        """
        Создает заказ с платежом.
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
