from django.contrib import admin
from .mixins import render_media_preview


class ProductMediaAdmin(admin.ModelAdmin):
    list_display = (
        "preview",
        "product",
        "variant",
        "type",
        "is_main",
        "position",
        "uploaded_at",
    )
    list_filter = ("type", "is_main")
    search_fields = ("product__name", "variant__sku", "url")
    list_editable = ("position", "is_main")
    readonly_fields = ("preview", "uploaded_at")

    fieldsets = (
        (None, {"fields": ("product", "variant", "type", "is_main")}),
        ("Медиа", {"fields": ("url", "preview", "position")}),
        ("Даты", {"fields": ("uploaded_at",), "classes": ("collapse",)}),
    )

    def preview(self, obj):
        return render_media_preview(obj)

    preview.short_description = "Предпросмотр"
