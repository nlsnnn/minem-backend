import logging

from django import forms

from apps.storage import StorageService
from ..models import ProductMedia

logger = logging.getLogger(__name__)


class ProductMediaForm(forms.ModelForm):
    """Форма для ProductMedia с автоматической загрузкой файлов в S3."""

    file_upload = forms.FileField(
        required=False,
        label="Загрузить файл",
        help_text="Загрузите изображение (jpg, jpeg, png, webp, gif, до 10 МБ)",
        widget=forms.ClearableFileInput(attrs={"accept": "image/*"}),
    )

    class Meta:
        model = ProductMedia
        fields = ["product", "variant", "type", "url", "position", "is_main"]
        widgets = {
            "url": forms.URLInput(
                attrs={
                    "placeholder": "Или введите URL вручную",
                    "class": "vURLField",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # URL не обязателен, если загружается файл
        if not self.instance.pk:
            self.fields["url"].required = False

    def clean(self):
        cleaned_data = super().clean()
        file_upload = cleaned_data.get("file_upload")
        url = cleaned_data.get("url")

        # Проверяем, что предоставлен либо файл, либо URL
        if not file_upload and not url:
            if not self.instance.pk:
                raise forms.ValidationError(
                    "Необходимо загрузить файл или указать URL"
                )

        return cleaned_data

    def save(self, commit=True):
        """Сохранение с автоматической загрузкой файла в S3."""
        instance = super().save(commit=False)
        file_upload = self.cleaned_data.get("file_upload")

        if file_upload:
            try:
                storage_service = StorageService()
                
                # Формируем путь с product_id для организации файлов
                product = self.cleaned_data.get("product")
                if product and product.pk:
                    path_prefix = f"products/{product.pk}"
                else:
                    path_prefix = "products/temp"
                
                result = storage_service.upload(
                    file=file_upload,
                    path_prefix=path_prefix,
                )
                instance.url = result.url
                
                logger.info(f"Файл загружен в S3: {result.url}")

            except Exception as e:
                logger.error(f"Ошибка загрузки файла в S3: {str(e)}")
                raise forms.ValidationError(f"Ошибка загрузки файла: {str(e)}")

        if commit:
            instance.save()

        return instance
