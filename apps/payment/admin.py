from django.contrib import admin
from django.utils.html import format_html
from config.admin import admin_site
from .models import Payment


class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "short_id",
        "order_link",
        "status_badge",
        "amount",
        "provider",
        "payment_date",
    )
    list_filter = ("status", "provider", "payment_date")
    search_fields = ("order__id", "provider_payment_id", "customer_email")
    readonly_fields = (
        "order",
        "provider",
        "provider_payment_id",
        "amount",
        "status",
        "payment_date",
    )
    date_hierarchy = "payment_date"

    fieldsets = (
        (
            "Информация о платеже",
            {
                "fields": (
                    "order",
                    "provider",
                    "provider_payment_id",
                    "status",
                    "amount",
                ),
            },
        ),
        (
            "Дополнительно",
            {
                "fields": ("payment_date",),
                "classes": ("collapse",),
            },
        ),
    )

    def short_id(self, obj):
        return str(obj.provider_payment_id)[:20] if obj.provider_payment_id else "-"

    short_id.short_description = "ID платежа"

    def order_link(self, obj):
        if obj.order:
            url = f"/admin/orders/order/{obj.order.id}/change/"
            return format_html('<a href="{}">{}</a>', url, str(obj.order.id)[:8])
        return "-"

    order_link.short_description = "Заказ"

    def status_badge(self, obj):
        colors = {
            "pending": "#FFA500",
            "succeeded": "#4CAF50",
            "failed": "#F44336",
            "canceled": "#777",
        }
        color = colors.get(obj.status, "#777")
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_badge.short_description = "Статус"

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        # Только для отмененных платежей
        if obj and obj.status == "canceled":
            return True
        return False


# Регистрируем только Payment, PaymentEvent скрыт
admin_site.register(Payment, PaymentAdmin)
