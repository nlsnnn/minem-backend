import uuid
from django.db import models
from apps.main.models import ProductVariant


class Order(models.Model):
    """
    Модель заказа
    """

    ORDER_STATUS_CHOICES = [
        ("awaiting_payment", "В ожидании оплаты"),
        ("paid", "Оплачен"),
        ("processing", "В обработке"),
        ("shipped", "Отправлен"),
        ("delivered", "Доставлен"),
        ("canceled", "Отменен"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID заказа",
    )
    status = models.CharField(
        max_length=50,
        verbose_name="Статус",
        choices=ORDER_STATUS_CHOICES,
        default="awaiting_payment",
    )
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Общая сумма"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        db_table = "orders"
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Заказ {self.id} от {self.customer_info.full_name}"


class OrderItem(models.Model):
    """
    Модель позиции заказа
    """

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Заказ",
    )
    product_variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="order_items",
        verbose_name="Вариант товара",
    )
    quantity = models.PositiveIntegerField(verbose_name="Количество")
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Цена за единицу"
    )

    class Meta:
        db_table = "order_items"
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказов"

    def __str__(self):
        return f"{self.product_variant.product.name} x {self.quantity}"


class OrderCustomer(models.Model):
    """
    Модель информации о клиенте заказа
    """

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="customer_info",
        verbose_name="Заказ",
        unique=True,
    )
    full_name = models.CharField(max_length=200, verbose_name="Имя клиента")
    email = models.EmailField(verbose_name="Email клиента")
    phone = models.CharField(max_length=20, verbose_name="Телефон клиента")
    city = models.CharField(max_length=100, verbose_name="Город", blank=True, null=True)
    shipping_address = models.TextField(verbose_name="Адрес доставки")
    comment = models.TextField(verbose_name="Комментарий", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        db_table = "order_customers"
        verbose_name = "Информация о клиенте заказа"
        verbose_name_plural = "Информация о клиентах заказов"

    def __str__(self):
        return f"{self.full_name} - {self.order.id}"
