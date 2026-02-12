import json
import logging
import time
import ipaddress

from functools import wraps
from django.conf import settings
from django.db import transaction, OperationalError, connection

from yookassa.domain.notification import WebhookNotification

from .models import Payment, PaymentEvent

logger = logging.getLogger(__name__)

# YooKassa официальные IP адреса для вебхуков
YOOKASSA_IPS = [
    "185.71.76.0/27",
    "185.71.77.0/27",
    "77.75.153.0/25",
    "77.75.156.11",
    "77.75.156.35",
    "77.75.154.128/25",
    "2a02:5180::/32",
]


def retry_on_db_locked(max_retries=3, delay=0.5):
    """Декоратор для повторной попытки при OperationalError (database is locked)"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except OperationalError as e:
                    last_exception = e
                    if "database is locked" in str(e):
                        if attempt < max_retries - 1:
                            wait_time = delay * (2**attempt)  # Exponential backoff
                            logger.warning(
                                f"Database locked on attempt {attempt + 1}/{max_retries}, "
                                f"retrying in {wait_time:.2f}s..."
                            )
                            time.sleep(wait_time)
                        else:
                            logger.error(
                                f"Database still locked after {max_retries} attempts, giving up"
                            )
                            raise
                    else:
                        raise
            if last_exception:
                raise last_exception

        return wrapper

    return decorator


class PaymentService:
    @staticmethod
    def get_client_ip(request):
        """Получение реального IP клиента с учетом прокси."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip

    @staticmethod
    def validate_yookassa_ip(ip_address: str) -> bool:
        """
        Проверка, что запрос пришел с официального IP YooKassa.
        """

        if settings.DEBUG:
            logger.warning(
                f"IP validation is DISABLED in DEBUG mode! Received IP: {ip_address}"
            )
            return True  # В dev режиме пропускаем все (закомментируйте в продакшене!)

        if not ip_address:
            return False

        try:
            client_ip = ipaddress.ip_address(ip_address)
            for allowed_range in YOOKASSA_IPS:
                if "/" in allowed_range:
                    if client_ip in ipaddress.ip_network(allowed_range):
                        return True
                else:
                    if str(client_ip) == allowed_range:
                        return True
            return False
        except ValueError:
            return False

    @staticmethod
    @retry_on_db_locked(max_retries=10, delay=0.5)
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
            # Проверяем дублирование БЕЗ транзакции (быстро)
            payment = Payment.objects.get(provider_payment_id=payment_id)

            if PaymentEvent.objects.filter(
                payment=payment, event_type=event_type
            ).exists():
                logger.warning(
                    f"Duplicate event {event_type} for payment {payment_id}, skipping"
                )
                return

            # Идемпотентность: если уже обработано, не обрабатываем повторно
            if event_type == "payment.succeeded" and payment.status == "succeeded":
                logger.warning(
                    f"Payment {payment_id} already succeeded, creating event only"
                )
                PaymentEvent.objects.create(
                    payment=payment,
                    event_type=event_type,
                    payload=payload,
                )
                return

            # КРИТИЧЕСКИ ВАЖНО: отделяем транзакцию БД от отправки email
            order = None
            with transaction.atomic():
                # Повторно получаем с блокировкой в транзакции
                payment = Payment.objects.select_for_update().get(
                    provider_payment_id=payment_id
                )

                if event_type == "payment.succeeded":
                    order = PaymentService._handle_payment_succeeded(payment, payload)
                elif event_type == "payment.canceled":
                    order = PaymentService._handle_payment_canceled(payment, payload)
                else:
                    logger.warning(f"Unhandled event type: {event_type}")
                    PaymentEvent.objects.create(
                        payment=payment,
                        event_type=event_type,
                        payload=payload,
                    )

            # Принудительно закрываем и сбрасываем соединение для SQLite
            if connection.vendor == "sqlite":
                connection.close()
                logger.debug("SQLite connection closed after transaction commit")

            # Email отправляем ПОСЛЕ успешного commit транзакции
            if order and event_type == "payment.succeeded":
                PaymentService._send_confirmation_email(order)
            elif order and event_type == "payment.canceled":
                PaymentService._send_cancellation_email(order)

        except Payment.DoesNotExist:
            logger.error(f"Payment {payment_id} not found in database")
            raise
        except Exception as e:
            logger.error(f"Error processing payment event: {e}", exc_info=True)
            raise

    @staticmethod
    def _handle_payment_succeeded(payment: Payment, payload: dict):
        """Обработка успешной оплаты (внутри транзакции)"""
        logger.info(
            f"[DB TRANSACTION] Starting payment success handler for {payment.provider_payment_id}"
        )

        payment.status = "succeeded"
        payment.save(update_fields=["status"])
        logger.info(
            f"[DB TRANSACTION] Payment {payment.provider_payment_id} status saved"
        )

        order = payment.order
        order.status = "paid"
        order.save(update_fields=["status"])
        logger.info(f"[DB TRANSACTION] Order {order.id} status saved")

        PaymentEvent.objects.create(
            payment=payment,
            event_type="payment.succeeded",
            payload=payload,
        )
        logger.info(f"[DB TRANSACTION] PaymentEvent created")

        return order

    @staticmethod
    def _send_confirmation_email(order):
        """Отправка email подтверждения (вне транзакции)"""
        try:
            from apps.orders.services.email_service import EmailService

            logger.info(
                f"Attempting to send confirmation email for order {order.id} to {order.customer_info.email}"
            )
            result = EmailService.send_order_confirmation(order)

            if result:
                logger.info(
                    f"Confirmation email sent successfully for order {order.id}"
                )
            else:
                logger.warning(f"Email service returned False for order {order.id}")

        except Exception as e:
            logger.error(
                f"Failed to send confirmation email for order {order.id}: {str(e)}",
                exc_info=True,
            )

    @staticmethod
    def _handle_payment_canceled(payment: Payment, payload: dict):
        """Обработка отмены платежа с возвратом товара на склад (внутри транзакции)"""
        logger.info(
            f"[DB TRANSACTION] Starting payment cancellation handler for {payment.provider_payment_id}"
        )

        payment.status = "canceled"
        payment.save(update_fields=["status"])

        order = payment.order
        order.status = "canceled"

        # Возврат товара на склад
        order_items = order.items.select_related("product_variant").all()
        for item in order_items:
            variant = item.product_variant
            variant.stock += item.quantity
            variant.save(update_fields=["stock"])

        order.save(update_fields=["status"])

        PaymentEvent.objects.create(
            payment=payment,
            event_type="payment.canceled",
            payload=payload,
        )

        logger.info(
            f"Payment {payment.provider_payment_id} canceled, order {order.id} canceled, stock restored"
        )

        return order  # Возвращаем order для отправки email

    @staticmethod
    def _send_cancellation_email(order):
        """Отправка email об отмене (вне транзакции)"""
        try:
            from apps.orders.services.email_service import EmailService

            EmailService.send_order_canceled(order, reason="Оплата была отменена")
            logger.info(f"Cancellation email sent for order {order.id}")
        except Exception as e:
            logger.error(
                f"Failed to send cancellation email for order {order.id}: {str(e)}",
                exc_info=True,
            )
