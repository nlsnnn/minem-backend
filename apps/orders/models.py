import uuid
from django.db import models
from apps.main.models import ProductVariant


class Order(models.Model):
    """
    Модель заказа
    """

    ORDER_STATUS_CHOICES = [
        ("awaiting_payment", "Ожидает оплаты"),
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
        verbose_name="Номер заказа",
    )
    status = models.CharField(
        max_length=50,
        verbose_name="Статус заказа",
        choices=ORDER_STATUS_CHOICES,
        default="awaiting_payment",
        help_text="Текущее состояние заказа",
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Общая сумма заказа",
        help_text="Сумма всех товаров в заказе",
    )
    payment_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Ссылка для оплаты",
        help_text="Ссылка на страницу оплаты",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        db_table = "orders"
        verbose_name = "Заказ клиента"
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
        verbose_name="Товар (размер)",
    )
    quantity = models.PositiveIntegerField(
        verbose_name="Количество штук", help_text="Сколько единиц товара заказано"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена за 1 шт.",
        help_text="Цена на момент оформления заказа",
    )

    class Meta:
        db_table = "order_items"
        verbose_name = "Позиция в заказе"
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
    full_name = models.CharField(
        max_length=200, verbose_name="Полное имя клиента", help_text="ФИО получателя"
    )
    email = models.EmailField(
        verbose_name="Email клиента", help_text="Для отправки уведомлений"
    )
    phone = models.CharField(
        max_length=20, verbose_name="Телефон клиента", help_text="Для связи по доставке"
    )
    city = models.CharField(max_length=100, verbose_name="Город", blank=True, null=True)
    shipping_address = models.TextField(
        verbose_name="Адрес доставки", help_text="Полный адрес с индексом"
    )
    comment = models.TextField(
        verbose_name="Комментарий",
        blank=True,
        null=True,
        help_text="Пожелания клиента к заказу",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        db_table = "order_customers"
        verbose_name = "Клиент (информация)"
        verbose_name_plural = "Клиенты"

    def __str__(self):
        return f"{self.full_name} - {self.order.id}"


class StockHistory(models.Model):
    """
    Модель истории изменений остатков товаров
    """

    ACTION_CHOICES = [
        ("order_created", "Резерв при создании заказа"),
        ("order_paid", "Списание при оплате заказа"),
        ("order_canceled", "Возврат при отмене заказа"),
        ("manual_adjustment", "Ручная корректировка"),
        ("restock", "Пополнение склада"),
    ]

    product_variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="stock_history",
        verbose_name="Вариант товара",
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_changes",
        verbose_name="Заказ",
        help_text="Заказ, связанный с этим изменением",
    )
    action = models.CharField(
        max_length=50, choices=ACTION_CHOICES, verbose_name="Тип операции"
    )
    quantity_change = models.IntegerField(
        verbose_name="Изменение количества",
        help_text="Отрицательное - списание, положительное - пополнение",
    )
    stock_before = models.PositiveIntegerField(
        verbose_name="Остаток до", help_text="Количество на складе до изменения"
    )
    stock_after = models.PositiveIntegerField(
        verbose_name="Остаток после", help_text="Количество на складе после изменения"
    )
    note = models.TextField(
        blank=True, verbose_name="Примечание", help_text="Дополнительная информация"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время")

    class Meta:
        db_table = "stock_history"
        verbose_name = "Запись в истории остатков"
        verbose_name_plural = "История остатков"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["product_variant", "-created_at"]),
            models.Index(fields=["order"]),
        ]

    def __str__(self):
        return f"{self.product_variant} {self.get_action_display()}: {self.quantity_change:+d}"
