import logging
from decimal import Decimal
from typing import Dict, List, Optional

from django.db import transaction
from rest_framework import serializers

from .models import Order, OrderItem, OrderCustomer
from apps.main.models import ProductVariant
from apps.payment.models import Payment
from apps.payment.provider import PaymentProviderBase, YookassaProvider

logger = logging.getLogger(__name__)


class OrderCreationService:
    """
    Сервис для создания заказов с платежами.
    """

    def __init__(self, payment_provider: Optional[PaymentProviderBase] = None):
        self.payment_provider = payment_provider or YookassaProvider()

    def create_order_with_payment(
        self,
        items_data: List[Dict],
        customer_data: Dict,
        return_url: Optional[str] = None,
    ) -> Order:
        """
        Создает заказ с платежом.
            items_data: Список товаров в заказе
            customer_data: Данные покупателя
            return_url: URL для возврата после оплаты
        """
        with transaction.atomic():
            variant_ids = [item["product_variant"].id for item in items_data]
            variants = ProductVariant.objects.select_for_update().filter(
                id__in=variant_ids,
                is_active=True,
            )

            # 2. Валидация и подсчет суммы
            validated_items, total_amount = self._validate_and_calculate_items(
                items_data, variants
            )

            # 3. Создаем заказ
            order = Order.objects.create(
                total_amount=total_amount, status="awaiting_payment"
            )

            # 4. Создаем информацию о клиенте
            customer = OrderCustomer.objects.create(order=order, **customer_data)

            # 5. Создаем позиции заказа и уменьшаем запасы
            self._create_order_items_and_update_stock(order, validated_items)

            # 6. Создаем платеж
            try:
                payment_url = self._create_payment(
                    order, total_amount, return_url, customer.email
                )
                order.payment_url = payment_url
                order.save(update_fields=["payment_url"])

                logger.info(f"Order {order.id} created successfully with payment")
                return order

            except Exception as e:
                logger.error(
                    f"Failed to create payment for order {order.id}: {e}", exc_info=True
                )
                raise serializers.ValidationError(
                    {"payment": "Не удалось создать платеж. Попробуйте позже."}
                )

    def _validate_and_calculate_items(
        self, items_data: List[Dict], variants
    ) -> tuple[List[Dict], Decimal]:
        """
        Проверяет доступность товаров и вычисляет общую стоимость.
        """
        validated_items = []
        total_amount = Decimal(0)

        for item_data in items_data:
            requested_variant = item_data["product_variant"]
            requested_quantity = int(item_data.get("quantity", 1))

            # Поиск варианта в заблокированных
            variant = next((v for v in variants if v.id == requested_variant.id), None)

            if not variant or not variant.is_active:
                logger.warning(f"Variant {requested_variant.id} is not available")
                raise serializers.ValidationError(
                    {"items": f"Товар (ID: {requested_variant.id}) недоступен"}
                )

            if variant.stock < requested_quantity:
                logger.warning(
                    f"Insufficient stock for variant {requested_variant.id}: "
                    f"requested={requested_quantity}, available={variant.stock}"
                )
                raise serializers.ValidationError(
                    {
                        "items": f"Недостаточно товара (ID: {requested_variant.id}). "
                        f"Доступно: {variant.stock}"
                    }
                )

            variant_price = variant.get_price()
            item_total = variant_price * requested_quantity
            total_amount += item_total

            validated_items.append(
                {
                    "product_variant": variant,
                    "quantity": requested_quantity,
                    "price": variant_price,
                }
            )

        return validated_items, total_amount

    def _create_order_items_and_update_stock(
        self, order: Order, validated_items: List[Dict]
    ) -> None:
        order_items = []

        for item_data in validated_items:
            variant = item_data["product_variant"]
            quantity = item_data["quantity"]

            # Создаем позицию заказа
            order_items.append(OrderItem(order=order, **item_data))

            # Уменьшаем запас
            variant.stock -= quantity
            variant.save(update_fields=["stock"])

        # Создаем все позиции одним запросом
        OrderItem.objects.bulk_create(order_items)

    def _create_payment(
        self,
        order: Order,
        amount: Decimal,
        return_url: Optional[str],
        customer_email: str,
    ) -> str:
        payment_result = self.payment_provider.create_payment(
            amount=amount,
            currency="RUB",
            order_id=str(order.id),
            return_url=return_url,
            customer_email=customer_email,
        )

        # Сохраняем запись о платеже
        Payment.objects.create(
            order=order,
            provider="yookassa",
            provider_payment_id=payment_result.payment_id,
            amount=amount,
            status="pending",
        )

        logger.info(
            f"Payment created for order {order.id}: {payment_result.payment_id}"
        )
        return payment_result.confirmation_url
