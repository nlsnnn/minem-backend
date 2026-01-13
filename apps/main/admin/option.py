from django.contrib import admin
from ..models import Option, OptionValue
from .inlines import OptionValueInline


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
