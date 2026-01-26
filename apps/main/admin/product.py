from django.contrib import admin
from django.utils.html import format_html
from ..models import Category, Product, ProductGroup
from .mixins import TimestampMixin
from .inlines import (
    ProductGroupCategoryInline,
    ProductVariantInline,
    ProductMediaInline,
)


@admin.register(Category)
class CategoryAdmin(TimestampMixin, admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("is_active",)


@admin.register(Product)
class ProductAdmin(TimestampMixin, admin.ModelAdmin):
    list_display = ("name", "group", "color", "price", "is_active", "created_at")
    list_filter = ("is_active", "group", "color")
    search_fields = ("name", "slug", "group__name", "color__name")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("is_active",)
    autocomplete_fields = ["group", "color"]
    inlines = [
        ProductVariantInline,
        ProductMediaInline,
    ]

    fieldsets = (
        (
            "Основная информация",
            {
                "fields": ("group", "color", "name", "slug", "price"),
                "description": "Укажите базовый товар, цвет и уникальное название для этого цвета.",
            },
        ),
        (
            "Публикация",
            {
                "fields": ("is_active",),
            },
        ),
        ("Даты", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


@admin.register(ProductGroup)
class ProductGroupAdmin(TimestampMixin, admin.ModelAdmin):
    list_display = ("name", "slug", "products_count", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("is_active",)
    inlines = [
        ProductGroupCategoryInline,
    ]

    fieldsets = (
        (
            "Название",
            {
                "fields": ("name", "slug", "is_active"),
                "description": "Название товара без учета цвета. Например: PUFFER JACKET gen 2",
            },
        ),
        (
            "Описание для покупателей",
            {
                "fields": ("excerpt", "description"),
                "description": "Краткое и полное описание товара",
            },
        ),
        (
            "Характеристики и уход",
            {
                "fields": (
                    "materials",
                    "care_instructions",
                    "size_chart",
                    "delivery_info",
                ),
                "description": "Техническая информация о товаре",
            },
        ),
        ("Даты", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def products_count(self, obj):
        count = obj.products.count()
        if count > 0:
            url = f"/admin/main/product/?group__id__exact={obj.id}"
            return format_html('<a href="{}">{} цвет(ов)</a>', url, count)
        return "0"

    products_count.short_description = "Количество цветов"
