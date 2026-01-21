from django.contrib import admin
from django.urls import reverse, path
from django.utils.html import format_html
from django.shortcuts import render, redirect
from django.contrib import messages
from ..models import Category, Product, ProductCategory
from .mixins import TimestampMixin
from .inlines import (
    ProductCategoryInline,
    ProductVariantInline,
    ProductContentInline,
    ProductMediaInline,
)
from .forms import BulkGenerateVariantsForm
from .services import generate_product_variants


@admin.register(Category)
class CategoryAdmin(TimestampMixin, admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("is_active",)


@admin.register(Product)
class ProductAdmin(TimestampMixin, admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "created_at")
    list_filter = ("is_active", "categories")
    search_fields = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("is_active",)
    inlines = [
        ProductCategoryInline,
        ProductVariantInline,
        ProductContentInline,
        ProductMediaInline,
    ]

    fieldsets = (
        (None, {"fields": ("name", "slug", "is_active")}),
        ("Описание", {"fields": ("excerpt", "description")}),
        ("Варианты", {"fields": ("variant_generator_link",)}),
        ("Даты", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def get_readonly_fields(self, request, obj=None):
        fields = list(super().get_readonly_fields(request, obj))
        fields.append("variant_generator_link")
        return fields

    def variant_generator_link(self, obj):
        if obj.pk:
            variants_count = obj.variants.count()
            url = reverse("admin:generate_variants", args=[obj.pk])
            
            button_text = "✨ Сгенерировать варианты" if variants_count == 0 else f"✨ Добавить варианты (есть {variants_count})"
            button_color = "#28a745" if variants_count == 0 else "#417690"
            
            return format_html(
                '<a class="button" href="{}" style="padding: 10px 15px; '
                'background: {}; color: white; text-decoration: none; '
                'border-radius: 4px; display: inline-block; font-weight: bold;">{}</a>',
                url,
                button_color,
                button_text,
            )
        return "Сначала сохраните товар, чтобы сгенерировать варианты."

    variant_generator_link.short_description = "Генератор вариантов"

    def get_urls(self):
        urls = super().get_urls()
        return [
            path(
                "<int:product_id>/generate-variants/",
                self.admin_site.admin_view(self.generate_variants_view),
                name="generate_variants",
            ),
        ] + urls

    def generate_variants_view(self, request, product_id):
        product = Product.objects.get(pk=product_id)

        if request.method == "POST":
            form = BulkGenerateVariantsForm(request.POST)
            if form.is_valid():
                created, skipped = generate_product_variants(
                    product=product,
                    option_values=form.cleaned_data["option_values"],
                    base_price=form.cleaned_data["base_price"],
                    stock=form.cleaned_data["stock"],
                    is_active=form.cleaned_data["is_active"],
                    copy_media=form.cleaned_data["copy_product_media"],
                )

                if created > 0:
                    messages.success(
                        request, f"Создано вариантов: {created}. Пропущено: {skipped}"
                    )
                elif skipped > 0:
                    messages.warning(request, "Все варианты уже существуют")
                else:
                    messages.error(request, "Невозможно создать варианты с выбранными значениями")

                return redirect("admin:main_product_change", product.id)
        else:
            form = BulkGenerateVariantsForm()

        return render(
            request,
            "admin/generate_variants.html",
            {
                "form": form,
                "product": product,
                "opts": self.model._meta,
                "title": f'Генератор вариантов для "{product.name}"',
            },
        )


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ("product", "category")
    list_filter = ("category",)
    search_fields = ("product__name", "category__name")
    autocomplete_fields = ["product", "category"]
