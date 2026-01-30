import logging
from typing import Optional

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from apps.orders.models import Order

logger = logging.getLogger(__name__)


class EmailService:
    """Сервис для отправки email уведомлений клиентам."""

    @staticmethod
    def send_order_confirmation(order: Order) -> bool:
        """
        Отправка email с подтверждением успешной оплаты заказа.

        Args:
            order: Объект заказа

        Returns:
            True если письмо отправлено, False если ошибка
        """
        try:
            customer = order.customer_info
            email_to = customer.email
            
            logger.info(
                f"Starting email send for order {order.id} to {email_to}. "
                f"EMAIL_BACKEND={settings.EMAIL_BACKEND}, "
                f"EMAIL_HOST={settings.EMAIL_HOST}:{settings.EMAIL_PORT}"
            )

            # Формируем контекст для шаблона
            context = {
                "order": order,
                "customer": customer,
                "items": order.items.select_related(
                    "product_variant__product__color",
                    "product_variant__size",
                ).all(),
                "site_name": "Minem",
                "frontend_url": settings.FRONTEND_URL,
            }
            
            logger.debug(f"Email context prepared for order {order.id}")

            # Рендерим HTML версию письма
            html_content = render_to_string(
                "emails/order_confirmation.html", context
            )

            # Создаем текстовую версию (fallback)
            text_content = strip_tags(html_content)

            # Формируем тему письма
            subject = f"Заказ #{order.id} успешно оплачен!"
            
            logger.debug(f"Email HTML rendered for order {order.id}, subject: {subject}")

            # Создаем письмо
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email_to],
            )

            # Прикрепляем HTML версию
            email.attach_alternative(html_content, "text/html")
            
            logger.debug(
                f"EmailMultiAlternatives created with from={settings.DEFAULT_FROM_EMAIL}, "
                f"to=[{email_to}], USE_TLS={settings.EMAIL_USE_TLS}, USE_SSL={settings.EMAIL_USE_SSL}"
            )

            # Отправляем
            email.send(fail_silently=False)

            logger.info(f"Email successfully sent to {email_to} for order {order.id}")
            return True

        except Exception as e:
            logger.error(
                f"Error sending email for order {order.id}: {str(e)}",
                exc_info=True,
            )
            return False

    @staticmethod
    def send_order_canceled(order: Order, reason: Optional[str] = None) -> bool:
        """
        Отправка email об отмене заказа.

        Args:
            order: Объект заказа
            reason: Причина отмены (опционально)

        Returns:
            True если письмо отправлено, False если ошибка
        """
        try:
            customer = order.customer_info
            email_to = customer.email

            logger.info(f"Starting cancellation email for order {order.id} to {email_to}")

            context = {
                "order": order,
                "customer": customer,
                "reason": reason or "Заказ не был оплачен в течение 2 часов",
                "site_name": "Minem",
                "frontend_url": settings.FRONTEND_URL,
            }

            html_content = render_to_string(
                "emails/order_canceled.html", context
            )
            text_content = strip_tags(html_content)

            subject = f"Заказ #{order.id} отменен"

            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email_to],
            )

            email.attach_alternative(html_content, "text/html")
            email.send(fail_silently=False)

            logger.info(
                f"Cancellation email successfully sent to {email_to} for order {order.id}"
            )
            return True

        except Exception as e:
            logger.error(
                f"Error sending cancellation email for order {order.id}: {str(e)}",
                exc_info=True,
            )
            return False
