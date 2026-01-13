from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from ..models import (
    ProductCategory,
    ProductContent,
    ProductMedia,
    ProductVariant,
    VariantOptionValue,
    OptionValue,
)


class ProductCategoryInline(admin.TabularInline):
    model = ProductCategory
    extra = 1


class ProductContentInline(admin.StackedInline):
    model = ProductContent
    extra = 0


class ProductMediaInline(admin.TabularInline):
    model = ProductMedia
    extra = 1
    fields = ("preview", "type", "url", "variant", "position", "is_main")
    readonly_fields = ("preview",)
    classes = ["collapse"]

    def preview(self, obj):
        from .mixins import render_media_preview

        return render_media_preview(obj, size=100)


class VariantOptionValueInline(admin.TabularInline):
    model = VariantOptionValue
    extra = 1


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0
    fields = ("sku_link", "price", "stock", "is_active", "options_display")
    readonly_fields = ("sku_link", "options_display")

    def sku_link(self, obj):
        if obj.pk:
            url = reverse("admin:main_productvariant_change", args=[obj.pk])
            return format_html('<a href="{}">{}</a>', url, obj.sku)
        return obj.sku

    sku_link.short_description = "Артикул"

    def options_display(self, obj):
        if obj.pk:
            opts = obj.option_values.select_related("option_value__option").all()
            if opts:
                return ", ".join(
                    f"{o.option_value.option.name}: {o.option_value.value}"
                    for o in opts
                )
        return "—"

    options_display.short_description = "Опции"


class OptionValueInline(admin.TabularInline):
    model = OptionValue
    extra = 1
