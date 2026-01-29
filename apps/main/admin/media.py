import logging

from django.contrib import admin

from apps.storage import StorageService
from .media_forms import ProductMediaForm
from .mixins import render_media_preview

logger = logging.getLogger(__name__)


class ProductMediaAdmin(admin.ModelAdmin):
    form = ProductMediaForm
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
        (
            "Медиа",
            {
                "fields": ("file_upload", "url", "preview", "position"),
                "description": "Загрузите файл или укажите URL",
            },
        ),
        ("Даты", {"fields": ("uploaded_at",), "classes": ("collapse",)}),
    )

    def preview(self, obj):
        return render_media_preview(obj)

    preview.short_description = "Предпросмотр"

    def delete_model(self, request, obj):
        """Удаление медиафайла с cleanup из S3 если не используется."""
        old_url = obj.url
        super().delete_model(request, obj)

        if old_url:
            try:
                storage_service = StorageService()
                storage_service.cleanup_unused(
                    file_url=old_url,
                    model_class=obj.__class__,
                    field_name="url",
                )
            except Exception as e:
                logger.error(f"Ошибка при удалении файла из S3: {str(e)}")

    def delete_queryset(self, request, queryset):
        """Массовое удаление с cleanup из S3."""
        urls_to_cleanup = list(queryset.values_list("url", flat=True))
        super().delete_queryset(request, queryset)

        storage_service = StorageService()
        for url in urls_to_cleanup:
            if url:
                try:
                    storage_service.cleanup_unused(
                        file_url=url,
                        model_class=queryset.model,
                        field_name="url",
                    )
                except Exception as e:
                    logger.error(f"Ошибка при удалении файла {url} из S3: {str(e)}")

