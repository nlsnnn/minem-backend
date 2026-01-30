import logging
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.orders.models import Order
from apps.payment.models import Payment

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Отмена неоплаченных заказов старше заданного времени"

    def add_arguments(self, parser):
        parser.add_argument(
            "--hours",
            type=int,
            default=2,
            help="Количество часов, после которых заказ считается просроченным (по умолчанию 2)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Только показать заказы без реальной отмены",
        )

    def handle(self, *args, **options):
        hours = options["hours"]
        dry_run = options["dry_run"]

        # Время отсечки
        cutoff_time = timezone.now() - timedelta(hours=hours)

        # Находим просроченные заказы
        expired_orders = Order.objects.filter(
            status="awaiting_payment",
            created_at__lt=cutoff_time,
        ).select_related("items")

        count = expired_orders.count()

        if count == 0:
            self.stdout.write(
                self.style.SUCCESS("Просроченных заказов не найдено")
            )
            return

        self.stdout.write(
            self.style.WARNING(
                f"Найдено {count} просроченных заказов (старше {hours}ч)"
            )
        )

        if dry_run:
            self.stdout.write(self.style.NOTICE("Режим dry-run: отмена не будет выполнена"))
            for order in expired_orders:
                self.stdout.write(
                    f"  - Заказ {order.id} от {order.created_at.strftime('%Y-%m-%d %H:%M')} "
                    f"на сумму {order.total_amount}₽"
                )
            return

        # Отменяем заказы и возвращаем товар на склад
        canceled_count = 0
        restored_items = 0

        for order in expired_orders:
            try:
                with transaction.atomic():
                    # Возвращаем товар на склад
                    for item in order.items.select_related("product_variant").all():
                        variant = item.product_variant
                        variant.stock += item.quantity
                        variant.save(update_fields=["stock"])
                        restored_items += 1

                    # Отменяем заказ
                    order.status = "canceled"
                    order.save(update_fields=["status", "updated_at"])

                    # Отменяем связанный платеж, если есть
                    Payment.objects.filter(
                        order=order,
                        status__in=["pending", "waiting_for_capture"]
                    ).update(status="canceled")

                    canceled_count += 1
                    logger.info(
                        f"Заказ {order.id} отменен автоматически (просрочен), "
                        f"возвращено позиций: {order.items.count()}"
                    )

                    # Отправка email клиенту
                    try:
                        from apps.orders.services.email_service import EmailService
                        
                        EmailService.send_order_canceled(
                            order,
                            reason="Заказ не был оплачен в течение 2 часов"
                        )
                    except Exception as email_error:
                        logger.error(
                            f"Ошибка при отправке email для заказа {order.id}: {str(email_error)}"
                        )

            except Exception as e:
                logger.error(
                    f"Ошибка при отмене заказа {order.id}: {str(e)}",
                    exc_info=True,
                )
                self.stdout.write(
                    self.style.ERROR(f"Ошибка при обработке заказа {order.id}: {str(e)}")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Успешно отменено {canceled_count} заказов, "
                f"возвращено {restored_items} позиций на склад"
            )
        )
