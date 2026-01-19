import json
import logging
from django.db import transaction

from yookassa.domain.notification import WebhookNotification

from .models import Payment, PaymentEvent

logger = logging.getLogger(__name__)


class PaymentService:
    @staticmethod
    def payment_acceptance(
        notification: WebhookNotification,
        payload: bytes,
    ) -> None:
        """
        Метод для обработки принятия оплаты заказа.
        Поддерживаемые события:
        - payment.succeeded: успешная оплата
        - payment.canceled: отмена платежа
        """
        payload = payload.decode("utf-8") if isinstance(payload, bytes) else payload
        payload = json.loads(payload) if isinstance(payload, str) else payload

        payment_id = notification.object.id
        event_type = notification.event

        logger.info(f"Processing payment event: {event_type} for payment {payment_id}")

        try:
            with transaction.atomic():
                payment = Payment.objects.select_for_update().get(
                    provider_payment_id=payment_id
                )

                # Проверка дублирования события
                if PaymentEvent.objects.filter(
                    payment=payment, event_type=event_type
                ).exists():
                    logger.warning(
                        f"Duplicate event {event_type} for payment {payment_id}, skipping"
                    )
                    return

                if event_type == "payment.succeeded":
                    PaymentService._handle_payment_succeeded(payment, payload)
                elif event_type == "payment.canceled":
                    PaymentService._handle_payment_canceled(payment, payload)
                else:
                    logger.warning(f"Unhandled event type: {event_type}")
                    PaymentEvent.objects.create(
                        payment=payment,
                        event_type=event_type,
                        payload=payload,
                    )

        except Payment.DoesNotExist:
            logger.error(f"Payment {payment_id} not found in database")
            raise
        except Exception as e:
            logger.error(f"Error processing payment event: {e}", exc_info=True)
            raise

    @staticmethod
    def _handle_payment_succeeded(payment: Payment, payload: dict) -> None:
        """Обработка успешной оплаты"""
        payment.status = "succeeded"
        payment.save()

        order = payment.order
        order.status = "paid"
        order.save()

        PaymentEvent.objects.create(
            payment=payment,
            event_type="payment.succeeded",
            payload=payload,
        )

        logger.info(
            f"Payment {payment.provider_payment_id} succeeded, order {order.id} marked as paid"
        )

    @staticmethod
    def _handle_payment_canceled(payment: Payment, payload: dict) -> None:
        """Обработка отмены платежа с возвратом товара на склад"""
        payment.status = "canceled"
        payment.save()

        order = payment.order
        order.status = "canceled"

        # Возврат товара на склад
        order_items = order.items.select_related("product_variant").all()
        for item in order_items:
            variant = item.product_variant
            variant.stock += item.quantity
            variant.save(update_fields=["stock"])

        order.save()

        PaymentEvent.objects.create(
            payment=payment,
            event_type="payment.canceled",
            payload=payload,
        )

        logger.info(
            f"Payment {payment.provider_payment_id} canceled, order {order.id} canceled, stock restored"
        )
