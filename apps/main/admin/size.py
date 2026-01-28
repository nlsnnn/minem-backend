from django.contrib import admin


class SizeAdmin(admin.ModelAdmin):
    list_display = ("name", "position", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)
    list_editable = ("position", "is_active")
    ordering = ["position", "name"]

    fieldsets = (
        (
            "Размеры",
            {
                "fields": ("name", "position", "is_active"),
                "description": "Создайте все используемые размеры, затем выбирайте их при создании вариантов товаров.",
            },
        ),
    )
