from django import forms
from ..models import Option


class BulkGenerateVariantsForm(forms.Form):
    options = forms.ModelMultipleChoiceField(
        queryset=Option.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Опции",
        help_text="Будут созданы все комбинации выбранных опций",
        required=True,
    )
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
    is_active = forms.BooleanField(
        initial=True, label="Активен", required=False
    )
    copy_product_media = forms.BooleanField(
        initial=True,
        label="Копировать медиа",
        help_text="Скопировать медиафайлы товара для всех вариантов",
        required=False,
    )
