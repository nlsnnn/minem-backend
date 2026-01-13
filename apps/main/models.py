import uuid
from django.db import models
from django.forms import ValidationError
from django.utils.text import slugify


class Category(models.Model):
    """
    Модель категории товаров
    """

    name = models.CharField(max_length=100, verbose_name="Название")
    slug = models.SlugField(unique=True, blank=True)
    is_active = models.BooleanField(default=False, verbose_name="Активна")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        db_table = "categories"
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    """
    Модель товара
    """

    name = models.CharField(max_length=250, verbose_name="Название")
    slug = models.SlugField(unique=True, blank=True)
    excerpt = models.CharField(
        max_length=500, blank=True, verbose_name="Краткое описание"
    )
    description = models.TextField(blank=True, verbose_name="Описание")
    is_active = models.BooleanField(default=False, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    categories = models.ManyToManyField(
        Category, through="ProductCategory", related_name="products"
    )

    class Meta:
        db_table = "products"
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ["name"]

    def __str__(self):
        return self.name


class ProductCategory(models.Model):
    """
    Модель категорий товара
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="product_categories",
        verbose_name="Товар",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="category_products",
        verbose_name="Категория",
    )

    class Meta:
        db_table = "product_categories"
        verbose_name = "Категория товара"
        verbose_name_plural = "Категории товара"
        unique_together = ("product", "category")
        indexes = [
            models.Index(fields=["product", "category"]),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.category.name}"


class Option(models.Model):
    """
    Модель опции товара
    """

    name = models.CharField(max_length=100, verbose_name="Название")

    class Meta:
        db_table = "product_options"
        verbose_name = "Опция товара"
        verbose_name_plural = "Опции товара"
        ordering = ["name"]

    def __str__(self):
        return self.name


class OptionValue(models.Model):
    """
    Модель значения опции товара
    """

    option = models.ForeignKey(
        Option, on_delete=models.CASCADE, related_name="values", verbose_name="Опция"
    )
    value = models.CharField(max_length=100, verbose_name="Значение")

    class Meta:
        db_table = "product_option_values"
        verbose_name = "Значение опции товара"
        verbose_name_plural = "Значения опций товара"
        ordering = ["value"]
        unique_together = ("option", "value")

    def __str__(self):
        return self.value


class ProductVariant(models.Model):
    """
    Модель варианта товара
    """

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="variants", verbose_name="Товар"
    )
    sku = models.CharField(
        max_length=100, unique=True, verbose_name="Артикул", blank=True
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    stock = models.PositiveIntegerField(default=0, verbose_name="Остаток")
    is_active = models.BooleanField(default=False, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")
    options = models.ManyToManyField(
        OptionValue, through="VariantOptionValue", related_name="variants"
    )

    class Meta:
        db_table = "product_variants"
        verbose_name = "Вариант товара"
        verbose_name_plural = "Варианты товара"
        ordering = ["sku"]

    def __str__(self):
        return f"{self.product.name} - {self.sku}"

    def save(self, *args, **kwargs):
        if not self.sku:
            # Автогенерация SKU если не указан
            base_sku = f"{self.product.slug}-{uuid.uuid4().hex[:8]}".upper()
            self.sku = base_sku
        super().save(*args, **kwargs)


class VariantOptionValue(models.Model):
    """
    Модель значения опции варианта
    """

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="option_values",
        verbose_name="Вариант",
    )
    option_value = models.ForeignKey(
        OptionValue,
        on_delete=models.CASCADE,
        related_name="variant_options",
        verbose_name="Значение опции",
    )

    class Meta:
        db_table = "variant_option_values"
        verbose_name = "Значение опции варианта"
        verbose_name_plural = "Значения опций варианта"
        unique_together = ("variant", "option_value")
        indexes = [
            models.Index(fields=["variant", "option_value"]),
        ]

    def __str__(self):
        return f"{self.variant.sku} - {self.option_value.value}"


class ProductContent(models.Model):
    """
    Модель содержания товара
    """

    CONTENT_TYPES = [
        ("care", "Care"),
        ("size_chart", "Size Chart"),
        ("materials", "Materials"),
        ("delivery", "Delivery Information"),
    ]

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="contents", verbose_name="Товар"
    )
    type = models.CharField(
        max_length=50, choices=CONTENT_TYPES, verbose_name="Тип содержания"
    )
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Содержание")
    position = models.PositiveIntegerField(default=0, verbose_name="Позиция")

    class Meta:
        db_table = "product_contents"
        verbose_name = "Содержание товара"
        verbose_name_plural = "Содержания товара"
        ordering = ["position"]

    def __str__(self):
        return f"{self.product.name} - {self.title}"


class ProductMedia(models.Model):
    """
    Модель медиа товара
    """

    MEDIA_TYPES = [
        ("image", "Image"),
        ("video", "Video"),
    ]

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="media", verbose_name="Товар"
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="media",
        null=True,
        blank=True,
        verbose_name="Вариант",
    )
    type = models.CharField(
        max_length=50, choices=MEDIA_TYPES, verbose_name="Тип медиа"
    )
    url = models.URLField(verbose_name="URL")  # S3
    position = models.PositiveIntegerField(default=0, verbose_name="Позиция")
    is_main = models.BooleanField(default=False, verbose_name="Основное")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Загружено")

    class Meta:
        db_table = "product_media"
        verbose_name = "Медиа товара"
        verbose_name_plural = "Медиа товара"
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.product.name} - {self.type} - {self.url}"

    def clean(self):
        if self.product_id and self.variant_id:
            if self.variant.product != self.product:
                raise ValidationError("Вариант должен принадлежать указанному товару.")

        if self.variant_id and not self.product_id:
            self.product = self.variant.product

        return super().clean()
