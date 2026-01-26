from django.contrib import admin
from django.forms import BaseInlineFormSet
from django.db import models
from ..models import (
    ProductGroupCategory,
    ProductMedia,
    ProductVariant,
)


class ProductGroupCategoryInline(admin.TabularInline):
    model = ProductGroupCategory
    extra = 1
    autocomplete_fields = ["category"]


class AutoPositionFormSetMixin:
    """Миксин для автоматической установки позиций в формсетах"""

    def _get_next_position(self, model, filters):
        if not filters:
            return 0
        max_pos = model.objects.filter(**filters).aggregate(models.Max("position"))[
            "position__max"
        ]
        return (max_pos or -1) + 1

    def save(self, commit=True):
        next_position = self._get_next_position(
            self.model, self._get_position_filters()
        )

        for form in self.forms:
            if (
                hasattr(form, "cleaned_data")
                and form.cleaned_data
                and not form.cleaned_data.get("DELETE")
                and form.instance.pk is None
                and form.instance.position == 0
            ):
                form.instance.position = next_position
                next_position += 1

        return super().save(commit=commit)


class ProductMediaFormSet(AutoPositionFormSetMixin, BaseInlineFormSet):
    def _get_position_filters(self):
        from ..models import Product as ProductModel

        parent = self.instance
        product = (
            parent
            if isinstance(parent, ProductModel)
            else getattr(parent, "product", None)
            if parent.pk
            else None
        )
        return {"product": product} if product and product.pk else {}


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


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0
    fields = ("size", "sku", "price", "stock", "is_active")
    readonly_fields = ("sku",)
    autocomplete_fields = ["size"]

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        if obj:
            formset.form.base_fields[
                "price"
            ].help_text = (
                f"Оставьте пустым для использования базовой цены ({obj.price})"
            )
        return formset
