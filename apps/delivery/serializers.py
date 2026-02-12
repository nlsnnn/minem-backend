from rest_framework import serializers


class CartItemSerializer(serializers.Serializer):
    """Сериализатор для товара в корзине."""
    product_variant = serializers.IntegerField(
        help_text="ID варианта товара"
    )
    quantity = serializers.IntegerField(
        min_value=1,
        max_value=100,
        default=1,
        help_text="Количество"
    )


class DeliveryCalculateSerializer(serializers.Serializer):
    """Сериализатор для расчета стоимости доставки."""
    items = CartItemSerializer(
        many=True,
        help_text="Список товаров в корзине"
    )
    address = serializers.CharField(
        required=True,
        min_length=5,
        help_text="Адрес доставки (город, улица, дом)"
    )
    tariff = serializers.ChoiceField(
        choices=[("time_interval", "До двери"), ("self_pickup", "Самовывоз")],
        default="time_interval",
        help_text="Тариф доставки"
    )


class DeliveryCalculateResponseSerializer(serializers.Serializer):
    """Сериализатор ответа с расчетом доставки."""
    cost = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Стоимость доставки в рублях"
    )
    delivery_days = serializers.IntegerField(
        help_text="Расчетное количество дней доставки"
    )
    currency = serializers.CharField(
        default="RUB",
        help_text="Валюта"
    )
