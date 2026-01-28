from django.contrib import admin


class ColorAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "position", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("position", "is_active")
    ordering = ["position", "name"]

    fieldsets = (
        (
            "Цвета товаров",
            {
                "fields": ("name", "slug", "position", "is_active"),
                "description": "Создайте цвета один раз, затем используйте их при создании товаров.",
            },
        ),
    )
