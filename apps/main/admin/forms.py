from django import forms
from ..models import Option, OptionValue


class BulkGenerateVariantsForm(forms.Form):
    option_values = forms.ModelMultipleChoiceField(
        queryset=OptionValue.objects.select_related('option').order_by('option__name', 'value'),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'option-values-checkboxes'}),
        label="Значения опций",
        help_text="Выберите конкретные значения для генерации вариантов (например: Красный, Синий из Цвета; S, M, L из Размера)",
        required=True,
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['option_values'].label_from_instance = lambda obj: f"{obj.option.name} - {obj.value}"
    base_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        label="Базовая цена",
        help_text="Цена для всех вариантов",
        required=True,
    )
    stock = forms.IntegerField(
        min_value=0,
        initial=0,
        label="Остаток",
        help_text="Количество на складе для всех вариантов",
        required=True,
    )
    is_active = forms.BooleanField(initial=True, label="Активен", required=False)
    copy_product_media = forms.BooleanField(
        initial=True,
        label="Копировать медиа",
        help_text="Скопировать медиафайлы товара для всех вариантов",
        required=False,
    )

    def clean_option_values(self):
        option_values = self.cleaned_data.get('option_values')
        if option_values:
            options = set(ov.option for ov in option_values)
            if len(options) < 1:
                raise forms.ValidationError(
                    "Выберите хотя бы одно значение опции"
                )
        return option_values
