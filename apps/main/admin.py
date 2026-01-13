from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import (
    Category,
    Product,
    ProductCategory,
    ProductContent,
    ProductMedia,
    Option,
    OptionValue,
    ProductVariant,
    VariantOptionValue,
)


class ProductCategoryInline(admin.TabularInline):
    model = ProductCategory
    extra = 1
    verbose_name = "Категория"
    verbose_name_plural = "Категории"


class ProductContentInline(admin.StackedInline):
    model = ProductContent
    extra = 0
    fields = ("type", "title", "content", "position")
    verbose_name = "Содержание"
    verbose_name_plural = "Содержание"


class ProductMediaInline(admin.TabularInline):
    model = ProductMedia
    extra = 1
    fields = ("media_preview", "type", "url", "variant", "position", "is_main")
    readonly_fields = ("media_preview",)
    verbose_name = "Медиа"
    verbose_name_plural = "Медиа файлы"
    classes = ["collapse"]

    def media_preview(self, obj):
        if obj.url:
            if obj.type == "image":
                return format_html(
                    '<img src="{}" style="max-width: 100px; max-height: 100px; border-radius: 4px;" />',
                    obj.url,
                )
            elif obj.type == "video":
                return format_html(
                    '<video width="150" height="100" controls style="border-radius: 4px;">'
                    '<source src="{}" type="video/mp4">'
                    "</video>",
                    obj.url,
                )
        return "—"

    media_preview.short_description = "Превью"


class VariantOptionValueInline(admin.TabularInline):
    model = VariantOptionValue
    extra = 1
    verbose_name = "Опция варианта"
    verbose_name_plural = "Опции варианта"


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0
    fields = ("sku_link", "price", "stock", "is_active", "variant_options")
    readonly_fields = ("sku_link", "variant_options", "created_at", "updated_at")
    verbose_name = "Вариант"
    verbose_name_plural = "Варианты"

    def sku_link(self, obj):
        if obj.pk:
            url = reverse("admin:main_productvariant_change", args=[obj.pk])
            return format_html('<a href="{}">{}</a>', url, obj.sku)
        return obj.sku

    sku_link.short_description = "Артикул"

    def variant_options(self, obj):
        if obj.pk:
            options = obj.option_values.select_related("option_value__option").all()
            if options:
                option_list = [
                    f"{opt.option_value.option.name}: {opt.option_value.value}"
                    for opt in options
                ]
                return ", ".join(option_list)
            return "—"
        return "—"

    variant_options.short_description = "Опции"


class OptionValueInline(admin.TabularInline):
    model = OptionValue
    extra = 1
    verbose_name = "Значение"
    verbose_name_plural = "Значения"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "created_at", "updated_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("is_active",)
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Основная информация", {"fields": ("name", "slug", "is_active")}),
        ("Даты", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "created_at", "updated_at")
    list_filter = ("is_active", "created_at", "categories")
    search_fields = ("name", "slug", "excerpt", "description")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("is_active",)
    readonly_fields = ("created_at", "updated_at")
    inlines = [
        ProductCategoryInline,
        ProductVariantInline,
        ProductContentInline,
        ProductMediaInline,
    ]

    fieldsets = (
        ("Основная информация", {"fields": ("name", "slug", "is_active")}),
        ("Описание", {"fields": ("excerpt", "description")}),
        ("Даты", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ("product", "category")
    list_filter = ("category",)
    search_fields = ("product__name", "category__name")
    autocomplete_fields = ["product", "category"]


@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    inlines = [OptionValueInline]


@admin.register(OptionValue)
class OptionValueAdmin(admin.ModelAdmin):
    list_display = ("option", "value")
    list_filter = ("option",)
    search_fields = ("value", "option__name")


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = (
        "variant_preview",
        "product",
        "sku",
        "price",
        "stock",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "created_at", "product")
    search_fields = ("sku", "product__name")
    list_editable = ("price", "stock", "is_active")
    readonly_fields = ("variant_media_preview", "created_at", "updated_at")
    inlines = [VariantOptionValueInline, ProductMediaInline]

    fieldsets = (
        ("Основная информация", {"fields": ("product", "sku", "is_active")}),
        ("Превью", {"fields": ("variant_media_preview",)}),
        ("Цена и остаток", {"fields": ("price", "stock")}),
        ("Даты", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def variant_preview(self, obj):
        """Превью для списка вариантов"""
        media = obj.media.filter(type="image", position=0).first()
        if media:
            return format_html(
                '<img src="{}" style="max-width: 50px; max-height: 50px; border-radius: 4px;" />',
                media.url,
            )
        # Если нет медиа у варианта, берем из товара
        product_media = obj.product.media.filter(type="image", is_main=True).first()
        if product_media:
            return format_html(
                '<img src="{}" style="max-width: 50px; max-height: 50px; border-radius: 4px; opacity: 0.6;" />',
                product_media.url,
            )
        return "—"

    variant_preview.short_description = "Фото"

    def variant_media_preview(self, obj):
        """Превью всех медиа варианта на странице редактирования"""
        media_items = obj.media.all()
        if not media_items:
            product_media = obj.product.media.filter(is_main=True).first()
            if product_media:
                return format_html(
                    '<div style="margin-bottom: 10px;">'
                    "<strong>Медиа товара (основное):</strong><br/>"
                    '<img src="{}" style="max-width: 200px; max-height: 200px; border-radius: 8px; margin-top: 8px;" />'
                    "</div>",
                    product_media.url,
                )
            return "Нет медиа"

        html_parts = []
        for media in media_items:
            if media.type == "image":
                html_parts.append(
                    f'<img src="{media.url}" style="max-width: 150px; max-height: 150px; border-radius: 8px; margin: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />'
                )
            elif media.type == "video":
                html_parts.append(
                    f'<video width="200" height="150" controls style="border-radius: 8px; margin: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">'
                    f'<source src="{media.url}" type="video/mp4">'
                    f"</video>"
                )

        return format_html(
            '<div style="display: flex; flex-wrap: wrap; gap: 8px;">{}</div>',
            format_html("".join(html_parts)),
        )

    variant_media_preview.short_description = "Медиа варианта"


@admin.register(VariantOptionValue)
class VariantOptionValueAdmin(admin.ModelAdmin):
    list_display = ("variant", "option_value")
    list_filter = ("option_value__option",)
    search_fields = ("variant__sku", "option_value__value")


@admin.register(ProductContent)
class ProductContentAdmin(admin.ModelAdmin):
    list_display = ("product", "type", "title", "position")
    list_filter = ("type", "product")
    search_fields = ("title", "content", "product__name")
    list_editable = ("position",)

    fieldsets = (
        ("Основная информация", {"fields": ("product", "type", "title", "position")}),
        ("Содержание", {"fields": ("content",)}),
    )


@admin.register(ProductMedia)
class ProductMediaAdmin(admin.ModelAdmin):
    list_display = (
        "media_preview",
        "product",
        "variant",
        "type",
        "is_main",
        "position",
        "uploaded_at",
    )
    list_filter = ("type", "is_main", "uploaded_at")
    search_fields = ("product__name", "variant__sku", "url")
    list_editable = ("position", "is_main")
    readonly_fields = ("media_preview", "uploaded_at")

    fieldsets = (
        ("Основная информация", {"fields": ("product", "variant", "type", "is_main")}),
        ("Медиа", {"fields": ("url", "media_preview", "position")}),
        ("Даты", {"fields": ("uploaded_at",), "classes": ("collapse",)}),
    )

    def media_preview(self, obj):
        if obj.url:
            if obj.type == "image":
                return format_html(
                    '<img src="{}" style="max-width: 150px; max-height: 150px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />',
                    obj.url,
                )
            elif obj.type == "video":
                return format_html(
                    '<video width="200" height="150" controls style="border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">'
                    '<source src="{}" type="video/mp4">'
                    "</video>",
                    obj.url,
                )
        return "—"

    media_preview.short_description = "Превью"
