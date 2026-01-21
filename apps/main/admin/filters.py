from django.contrib import admin
from ..models import Option, OptionValue


class OptionValueFilter(admin.SimpleListFilter):
    title = 'опции'
    parameter_name = 'option_value'

    def lookups(self, request, model_admin):
        """Группируем опции по названиям для удобства"""
        options = Option.objects.prefetch_related('values').all()
        choices = []
        for option in options:
            values = option.values.all()
            if values:
                choices.append((f'option_{option.id}', f'─── {option.name} ───'))
                for value in values:
                    choices.append((f'value_{value.id}', f'  • {value.value}'))
        return choices

    def queryset(self, request, queryset):
        if self.value() and self.value().startswith('value_'):
            value_id = self.value().replace('value_', '')
            return queryset.filter(
                option_values__option_value__id=value_id
            ).distinct()
        return queryset
