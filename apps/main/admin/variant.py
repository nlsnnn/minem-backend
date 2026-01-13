from django.contrib import admin
from django.shortcuts import render
from django.utils.html import format_html
from ..models import ProductVariant, VariantOptionValue, ProductMedia
from .mixins import TimestampMixin, render_image_preview
from .inlines import VariantOptionValueInline, ProductMediaInline


@admin.action(description="Массовое обновление цен")
def bulk_update_price(modeladmin, request, queryset):
    if "apply" in request.POST:
        new_price = request.POST.get("new_price")
        if new_price:
            count = queryset.update(price=new_price)
            modeladmin.message_user(request, f"Обновлено {count} цен")
            return

    return render(
        request,
        "admin/bulk_update_price.html",
        {
            "variants": queryset,
            "action": "bulk_update_price",
            "title": "Массовое обновление цен",
        },
    )


@admin.action(description="Массовое обновление остатков")
def bulk_update_stock(modeladmin, request, queryset):
    if "apply" in request.POST:
        new_stock = request.POST.get("new_stock")
        if new_stock:
            count = queryset.update(stock=new_stock)
            modeladmin.message_user(request, f"Обновлено {count} остатков")
            return

    return render(
        request,
        "admin/bulk_update_stock.html",
        {
            "variants": queryset,
            "action": "bulk_update_stock",
            "title": "Массовое обновление остатков",
        },
    )


@admin.action(description="Дублировать вариант")
def duplicate_variant(modeladmin, request, queryset):
    count = 0
    for variant in queryset:
        new_sku = f"{variant.sku}-COPY-{variant.id}"
        new_variant = ProductVariant.objects.create(
            product=variant.product,
            sku=new_sku,
            price=variant.price,
            stock=0,
            is_active=False,
        )

        for option_value in variant.option_values.all():
            VariantOptionValue.objects.create(
                variant=new_variant, option_value=option_value.option_value
            )

        for media in variant.media.all():
            ProductMedia.objects.create(
                product=new_variant.product,
                variant=new_variant,
                type=media.type,
                url=media.url,
                position=media.position,
                is_main=False,
            )

        count += 1

    modeladmin.message_user(request, f"Дублировано вариантов: {count}")


@admin.register(ProductVariant)
class ProductVariantAdmin(TimestampMixin, admin.ModelAdmin):
    list_display = (
        "preview",
        "product",
        "sku",
        "price",
        "stock",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "product")
    search_fields = ("sku", "product__name")
    list_editable = ("price", "stock", "is_active")
    inlines = [VariantOptionValueInline, ProductMediaInline]
    actions = [bulk_update_price, bulk_update_stock, duplicate_variant]

    fieldsets = (
        (None, {"fields": ("product", "sku", "sku_suggestion", "is_active")}),
        ("Цена", {"fields": ("price", "stock")}),
        ("Медиа", {"fields": ("media_gallery",)}),
        ("Даты", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def get_readonly_fields(self, request, obj=None):
        fields = list(super().get_readonly_fields(request, obj))
        fields.extend(["media_gallery", "sku_suggestion"])
        return fields

    def preview(self, obj):
        media = obj.media.filter(type="image").first()
        if media:
            return render_image_preview(media.url, 50)

        product_media = obj.product.media.filter(type="image", is_main=True).first()
        if product_media:
            return format_html(
                '<img src="{}" style="max-width: 50px; max-height: 50px; '
                'border-radius: 4px; opacity: 0.6;" />',
                product_media.url,
            )
        return "—"

    preview.short_description = "Изображение"

    def sku_suggestion(self, obj):
        if obj.pk and obj.product:
            option_values = obj.option_values.select_related(
                "option_value__option"
            ).all()
            if option_values:
                codes = "-".join(
                    ov.option_value.value[:3].upper() for ov in option_values
                )
                suggestion = f"{obj.product.slug}-{codes}"
                return format_html(
                    '<code style="background: #f0f0f0; padding: 5px 10px; '
                    'border-radius: 4px;">{}</code>',
                    suggestion,
                )
        return "Автоматически сгенерированное предложение SKU на основе опций."

    sku_suggestion.short_description = "Предложение SKU"

    def media_gallery(self, obj):
        media_items = obj.media.all().order_by("position")
        if not media_items:
            product_media = obj.product.media.filter(is_main=True).first()
            if product_media:
                return format_html(
                    "<div><strong>Медиа продукта:</strong><br/>"
                    '<img src="{}" style="max-width: 200px; max-height: 200px; '
                    'border-radius: 8px; margin-top: 8px;" /></div>',
                    product_media.url,
                )
            return "Нет медиафайлов."

        html_parts = []
        for media in media_items:
            if media.type == "image":
                html_parts.append(
                    f'<img src="{media.url}" style="max-width: 150px; '
                    f'max-height: 150px; border-radius: 8px; margin: 4px;" />'
                )
            elif media.type == "video":
                html_parts.append(
                    f'<video width="200" height="150" controls style="border-radius: 8px; margin: 4px;">'
                    f'<source src="{media.url}" type="video/mp4"></video>'
                )

        return format_html(
            '<div style="display: flex; flex-wrap: wrap; gap: 8px;">{}</div>',
            format_html("".join(html_parts)),
        )

    media_gallery.short_description = "Медиа галерея"


@admin.register(VariantOptionValue)
class VariantOptionValueAdmin(admin.ModelAdmin):
    list_display = ("variant", "option_value")
    list_filter = ("option_value__option",)
    search_fields = ("variant__sku", "option_value__value")
