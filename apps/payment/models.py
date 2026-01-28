from django.db import models
from apps.orders.models import Order


class Payment(models.Model):
    """
    Модель платежа
    """

    PAYMENT_STATUS_CHOICES = [
        ("pending", "В ожидании"),
        ("succeeded", "Завершен"),
        ("canceled", "Отменен"),
    ]

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="Заказ",
    )
    provider = models.CharField(max_length=100, verbose_name="Провайдер платежа")
    provider_payment_id = models.CharField(
        max_length=100,
        verbose_name="ID платежа у провайдера",
        unique=True,
        db_index=True,
    )

    amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Сумма платежа"
    )
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата платежа")
    status = models.CharField(
        max_length=50,
        verbose_name="Статус платежа",
        choices=PAYMENT_STATUS_CHOICES,
        default="pending",
    )

    class Meta:
        db_table = "payments"
        verbose_name = "Платеж клиента"
        verbose_name_plural = "Платежи"
        ordering = ["-payment_date"]
        indexes = [
            models.Index(fields=["-payment_date"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"Платеж {self.id} - Заказ {self.order.id} - Сумма {self.amount}"


class PaymentEvent(models.Model):
    """
    Модель события платежа
    """

    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name="events",
        verbose_name="Платеж",
    )
    event_type = models.CharField(max_length=100, verbose_name="Тип события")
    event_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата события")
    payload = models.JSONField(verbose_name="Данные события")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")

    class Meta:
        db_table = "payment_events"
        verbose_name = "Событие платежа"
        verbose_name_plural = "События платежей"
        ordering = ["-event_date"]
        indexes = [
            models.Index(fields=["payment", "event_type"]),
            models.Index(fields=["-event_date"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["payment", "event_type"], name="unique_payment_event"
            )
        ]

    def __str__(self):
        return f"Событие {self.event_type} для Платежа {self.payment.id}"
