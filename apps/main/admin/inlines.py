from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.forms import BaseInlineFormSet
from django.db import models
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


class AutoPositionFormSetMixin:
    """Миксин для автоматической установки позиций в формсетах"""
    
    def _get_next_position(self, model, filters):
        if not filters:
            return 0
        max_pos = model.objects.filter(**filters).aggregate(
            models.Max('position'))['position__max']
        return (max_pos or -1) + 1

    def save(self, commit=True):
        next_position = self._get_next_position(
            self.model, 
            self._get_position_filters()
        )
        
        for form in self.forms:
            if (hasattr(form, 'cleaned_data') and form.cleaned_data and 
                not form.cleaned_data.get('DELETE') and 
                form.instance.pk is None and form.instance.position == 0):
                form.instance.position = next_position
                next_position += 1
        
        return super().save(commit=commit)


class ProductContentFormSet(AutoPositionFormSetMixin, BaseInlineFormSet):
    def _get_position_filters(self):
        return {'product': self.instance} if self.instance and self.instance.pk else {}


class ProductMediaFormSet(AutoPositionFormSetMixin, BaseInlineFormSet):
    def _get_position_filters(self):
        from ..models import Product as ProductModel
        
        parent = self.instance
        product = (parent if isinstance(parent, ProductModel) 
                   else getattr(parent, 'product', None) if parent.pk else None)
        return {'product': product} if product and product.pk else {}


class ProductContentInline(admin.StackedInline):
    model = ProductContent
    formset = ProductContentFormSet
    extra = 0


class ProductMediaInline(admin.TabularInline):
    model = ProductMedia
    formset = ProductMediaFormSet
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
    fields = ("sku_link", "options_display", "price", "stock", "is_active")
    readonly_fields = ("sku_link", "options_display")

    def sku_link(self, obj):
        if obj.pk:
            url = reverse("admin:main_productvariant_change", args=[obj.pk])
            return format_html('<a href="{}">{}</a>', url, obj.sku)
        return obj.sku

    sku_link.short_description = "Артикул"

    def options_display(self, obj):
        if not obj.pk:
            return "—"
        
        opts = obj.option_values.select_related("option_value__option").all()
        if not opts:
            return "—"
        
        items = [
            f'<span style="background: #e8f4f8; color: #417690; '
            f'padding: 2px 6px; border-radius: 3px; margin: 1px; '
            f'display: inline-block; font-size: 11px; font-weight: 500;">'
            f'{o.option_value.value}</span>'
            for o in opts
        ]
        return format_html("".join(items))

    options_display.short_description = "Опции"


class OptionValueInline(admin.TabularInline):
    model = OptionValue
    extra = 1
    extra = 1
