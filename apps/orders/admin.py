from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from config.admin import admin_site
from .models import Order, OrderItem, OrderCustomer, StockHistory


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ("product_variant", "quantity", "price", "subtotal")
    readonly_fields = ("subtotal",)
    autocomplete_fields = ["product_variant"]

    def subtotal(self, obj):
        if obj.pk:
            return f"{obj.quantity * obj.price:.2f} руб."
        return "-"

    subtotal.short_description = "Сумма"


class OrderCustomerInline(admin.StackedInline):
    model = OrderCustomer
    extra = 0
    fields = (
        ("full_name", "phone"),
        "email",
        ("city", "shipping_address"),
        "comment",
    )


class StockHistoryInline(admin.TabularInline):
    model = StockHistory
    extra = 0
    fields = (
        "action",
        "quantity_change",
        "stock_before",
        "stock_after",
        "created_at",
        "note",
    )
    readonly_fields = (
        "action",
        "quantity_change",
        "stock_before",
        "stock_after",
        "created_at",
    )
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "short_id",
        "customer_name",
        "status_badge",
        "total_amount",
        "delivery_cost_display",
        "items_count",
        "created_at",
    )
    list_filter = ("status", "delivery_method", "created_at")
    search_fields = (
        "id",
        "customer_info__full_name",
        "customer_info__email",
        "customer_info__phone",
    )
    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "payment_link",
    )
    date_hierarchy = "created_at"
    inlines = [OrderCustomerInline, OrderItemInline, StockHistoryInline]
    actions = [
        "mark_as_paid",
        "mark_as_processing",
        "mark_as_shipped",
        "mark_as_delivered",
        "mark_as_canceled",
    ]

    fieldsets = (
        (
            "Информация о заказе",
            {
                "fields": ("id", "status", "total_amount"),
                "description": "Основная информация о заказе",
            },
        ),
        (
            "Доставка",
            {
                "fields": ("delivery_cost", "delivery_method"),
                "classes": ("collapse",),
            },
        ),
        (
            "Оплата",
            {
                "fields": ("payment_link",),
                "classes": ("collapse",),
            },
        ),
        (
            "Служебная информация",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def short_id(self, obj):
        return str(obj.id)[:8]

    short_id.short_description = "Номер заказа"

    def customer_name(self, obj):
        try:
            return obj.customer_info.full_name
        except OrderCustomer.DoesNotExist:
            return "-"

    customer_name.short_description = "Клиент"

    def status_badge(self, obj):
        colors = {
            "awaiting_payment": "#FFA500",
            "paid": "#4CAF50",
            "processing": "#2196F3",
            "shipped": "#9C27B0",
            "delivered": "#4CAF50",
            "canceled": "#F44336",
        }
        color = colors.get(obj.status, "#777")
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_badge.short_description = "Статус"

    def items_count(self, obj):
        count = obj.items.count()
        return f"{count} поз."

    items_count.short_description = "Товаров"

    def payment_link(self, obj):
        if obj.payment_url:
            return format_html(
                '<a href="{}" target="_blank">Открыть ссылку на оплату</a>',
                obj.payment_url,
            )
        return "Не создана"

    payment_link.short_description = "Ссылка для оплаты"

    def delivery_cost_display(self, obj):
        """Отображение стоимости доставки"""
        if obj.delivery_cost > 0:
            return f"{obj.delivery_cost} ₽"
        return "Бесплатно"

    delivery_cost_display.short_description = "Доставка"

    # Actions
    def mark_as_paid(self, request, queryset):
        updated = queryset.update(status="paid")
        self.message_user(request, f"{updated} заказ(ов) помечено как оплаченные")

    mark_as_paid.short_description = "Отметить как Оплачен"

    def mark_as_processing(self, request, queryset):
        updated = queryset.update(status="processing")
        self.message_user(request, f"{updated} заказ(ов) переведено в обработку")

    mark_as_processing.short_description = "Отметить как В обработке"

    def mark_as_shipped(self, request, queryset):
        updated = queryset.update(status="shipped")
        self.message_user(request, f"{updated} заказ(ов) помечено как отправленные")

    mark_as_shipped.short_description = "Отметить как Отправлен"

    def mark_as_delivered(self, request, queryset):
        updated = queryset.update(status="delivered")
        self.message_user(request, f"{updated} заказ(ов) помечено как доставленные")

    mark_as_delivered.short_description = "Отметить как Доставлен"

    def mark_as_canceled(self, request, queryset):
        updated = queryset.update(status="canceled")
        self.message_user(request, f"{updated} заказ(ов) отменено")

    mark_as_canceled.short_description = "Отметить как Отменен"

    def has_add_permission(self, request):
        return False


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order_short_id", "product_info", "quantity", "price", "total")
    list_filter = ("order__status", "order__created_at")
    search_fields = (
        "order__id",
        "product_variant__product__name",
        "product_variant__sku",
    )
    readonly_fields = ("order", "product_variant", "quantity", "price", "total")

    def order_short_id(self, obj):
        return str(obj.order.id)[:8]

    order_short_id.short_description = "Заказ"

    def product_info(self, obj):
        return f"{obj.product_variant.product.name} ({obj.product_variant.size.name})"

    product_info.short_description = "Товар"

    def total(self, obj):
        return f"{obj.quantity * obj.price:.2f} руб."

    total.short_description = "Сумма"

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class OrderCustomerAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "phone", "city", "order_short_id")
    search_fields = ("full_name", "email", "phone", "city", "order__id")
    readonly_fields = ("order", "created_at", "updated_at")

    fieldsets = (
        (
            "Контактная информация",
            {
                "fields": (("full_name", "phone"), "email"),
            },
        ),
        (
            "Адрес доставки",
            {
                "fields": ("city", "shipping_address"),
            },
        ),
        (
            "Дополнительно",
            {
                "fields": ("comment",),
            },
        ),
        (
            "Служебная информация",
            {
                "fields": ("order", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def order_short_id(self, obj):
        return str(obj.order.id)[:8]

    order_short_id.short_description = "Заказ"

    def has_add_permission(self, request):
        return False


class StockHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "product_info",
        "action_badge",
        "change_display",
        "stock_before",
        "stock_after",
        "order_link",
    )
    list_filter = ("action", "created_at", "product_variant__product__group")
    search_fields = (
        "product_variant__product__name",
        "product_variant__sku",
        "order__id",
        "note",
    )
    readonly_fields = (
        "product_variant",
        "order",
        "action",
        "quantity_change",
        "stock_before",
        "stock_after",
        "created_at",
    )
    date_hierarchy = "created_at"

    fieldsets = (
        (
            "Информация об изменении",
            {
                "fields": (
                    "product_variant",
                    "action",
                    "quantity_change",
                    ("stock_before", "stock_after"),
                ),
            },
        ),
        (
            "Связанный заказ",
            {
                "fields": ("order",),
            },
        ),
        (
            "Дополнительно",
            {
                "fields": ("note", "created_at"),
            },
        ),
    )

    def product_info(self, obj):
        return f"{obj.product_variant.product.name} ({obj.product_variant.size.name})"

    product_info.short_description = "Товар"

    def action_badge(self, obj):
        colors = {
            "order_created": "#FFA500",
            "order_paid": "#F44336",
            "order_canceled": "#4CAF50",
            "manual_adjustment": "#2196F3",
            "restock": "#4CAF50",
        }
        color = colors.get(obj.action, "#777")
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_action_display(),
        )

    action_badge.short_description = "Операция"

    def change_display(self, obj):
        color = "#4CAF50" if obj.quantity_change > 0 else "#F44336"
        formatted_value = f"{obj.quantity_change:+d}"
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            formatted_value,
        )

    change_display.short_description = "Изменение"

    def order_link(self, obj):
        if obj.order:
            url = reverse("admin:orders_order_change", args=[obj.order.id])
            return format_html('<a href="{}">{}</a>', url, str(obj.order.id)[:8])
        return "-"

    order_link.short_description = "Заказ"

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# Регистрируем модели в кастомной админке
admin_site.register(Order, OrderAdmin)
admin_site.register(OrderItem, OrderItemAdmin)
admin_site.register(OrderCustomer, OrderCustomerAdmin)
admin_site.register(StockHistory, StockHistoryAdmin)
