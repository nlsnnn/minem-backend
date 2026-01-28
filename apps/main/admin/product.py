from django.contrib import admin
from django.utils.html import format_html
from .mixins import TimestampMixin
from .inlines import (
    ProductGroupCategoryInline,
    ProductVariantInline,
    ProductMediaInline,
)


class CategoryAdmin(TimestampMixin, admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("is_active",)


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
                "description": (
                    "<strong>Создание товара:</strong><br>"
                    "1. Сначала выберите <strong>базовый товар</strong> (если нужного нет - создайте в разделе 'Базовые товары')<br>"
                    "2. Выберите <strong>цвет</strong> (если нужного нет - создайте в разделе 'Цвета')<br>"
                    "3. Укажите <strong>полное название</strong> с цветом, например: 'HOODIE Basic черный'<br>"
                    "4. URL сгенерируется автоматически из названия<br>"
                    "5. Укажите цену (одинаковую для всех размеров этого цвета)"
                ),
            },
        ),
        (
            "Публикация",
            {
                "fields": ("is_active",),
                "description": "Поставьте галочку чтобы товар появился на сайте. После сохранения добавьте размеры ниже.",
            },
        ),
        ("Даты", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


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
                "description": (
                    "<strong>Базовый товар</strong> - это товар без учета цвета.<br>"
                    "Например: 'PUFFER JACKET gen 2' или 'HOODIE Basic'<br><br>"
                    "Один базовый товар может иметь несколько цветов.<br>"
                    "URL сгенерируется автоматически из названия."
                ),
            },
        ),
        (
            "Описание для покупателей",
            {
                "fields": ("excerpt", "description"),
                "description": (
                    "<strong>Краткое описание</strong> показывается в каталоге<br>"
                    "<strong>Полное описание</strong> показывается на странице товара"
                ),
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
                "description": (
                    "Техническая информация о товаре:<br>"
                    "• <strong>Состав</strong>: материалы изделия<br>"
                    "• <strong>Уход</strong>: рекомендации по стирке<br>"
                    "• <strong>Размерная сетка</strong>: таблица размеров<br>"
                    "• <strong>Доставка</strong>: информация о сроках"
                ),
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
