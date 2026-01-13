from django.contrib import admin
from django.utils.html import format_html


class TimestampMixin:
    def get_readonly_fields(self, request, obj=None):
        fields = list(super().get_readonly_fields(request, obj))
        if hasattr(self.model, "created_at"):
            fields.append("created_at")
        if hasattr(self.model, "updated_at"):
            fields.append("updated_at")
        return fields


def render_image_preview(url, size=50):
    if not url:
        return "—"
    return format_html(
        '<img src="{}" style="max-width: {}px; max-height: {}px; border-radius: 4px;" />',
        url,
        size,
        size,
    )


def render_media_preview(obj, size=150):
    if not obj.url:
        return "—"

    if obj.type == "image":
        return render_image_preview(obj.url, size)

    if obj.type == "video":
        return format_html(
            '<video width="{}" height="{}" controls style="border-radius: 4px;">'
            '<source src="{}" type="video/mp4"></video>',
            size + 50,
            size,
            obj.url,
        )
    return "—"
