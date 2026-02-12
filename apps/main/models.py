from django.db import models
from django.forms import ValidationError
from django.utils.text import slugify


class Color(models.Model):
    """
    Модель цвета товара
    """

    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Название цвета",
        help_text="Например: Черный, Белый, Молочный",
    )
    slug = models.SlugField(
        unique=True,
        blank=True,
        verbose_name="URL (латиницей)",
        help_text="Будет сгенерирован автоматически",
    )
    position = models.PositiveIntegerField(
        default=0,
        verbose_name="Порядок отображения",
        help_text="Чем меньше число, тем выше в списке",
    )
    is_active = models.BooleanField(default=True, verbose_name="Показывать на сайте")

    class Meta:
        db_table = "colors"
        verbose_name = "Цвет (справочник)"
        verbose_name_plural = "Цвета"
        ordering = ["position", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Category(models.Model):
    """
    Модель категории товаров
    """

    name = models.CharField(
        max_length=100,
        verbose_name="Название категории",
        help_text="Например: Свитшоты, Куртки, Футболки",
    )
    slug = models.SlugField(
        unique=True,
        blank=True,
        verbose_name="URL (латиницей)",
        help_text="Будет сгенерирован автоматически",
    )
    is_active = models.BooleanField(default=False, verbose_name="Показывать на сайте")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        db_table = "categories"
        verbose_name = "Категория товаров"
        verbose_name_plural = "Категории"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Size(models.Model):
    """
    Модель размера
    """

    name = models.CharField(
        max_length=10,
        unique=True,
        verbose_name="Размер",
        help_text="Например: XS, S, M, L, XL, XXL",
    )
    position = models.PositiveIntegerField(
        default=0,
        verbose_name="Порядок отображения",
        help_text="Чем меньше число, тем выше в списке",
    )
    is_active = models.BooleanField(default=True, verbose_name="Использовать")

    class Meta:
        db_table = "sizes"
        verbose_name = "Размер (справочник)"
        verbose_name_plural = "Размеры"
        ordering = ["position", "name"]

    def __str__(self):
        return self.name


class ProductGroup(models.Model):
    """
    Модель группы товаров (товар без цвета)
    """

    name = models.CharField(
        max_length=250,
        verbose_name="Название товара",
        help_text="Например: PUFFER JACKET gen 2",
    )
    slug = models.SlugField(
        unique=True,
        blank=True,
        verbose_name="URL (латиницей)",
        help_text="Будет сгенерирован автоматически",
    )
    excerpt = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Краткое описание",
        help_text="Показывается в карточке товара в каталоге",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Полное описание",
        help_text="Подробное описание товара",
    )
    materials = models.TextField(
        blank=True,
        verbose_name="Состав и материалы",
        help_text="Например: 100% хлопок, пенополиуретан",
    )
    care_instructions = models.TextField(
        blank=True,
        verbose_name="Уход за изделием",
        help_text="Например: Стирать при 30°, не отбеливать, гладить при низкой температуре",
    )
    size_chart = models.TextField(
        blank=True,
        verbose_name="Размерная сетка",
        help_text="Таблица размеров для этого товара",
    )
    delivery_info = models.TextField(
        blank=True,
        verbose_name="Информация о доставке",
        help_text="Сроки и условия доставки",
    )
    is_active = models.BooleanField(default=False, verbose_name="Показывать на сайте")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    categories = models.ManyToManyField(
        Category, through="ProductGroupCategory", related_name="product_groups"
    )

    class Meta:
        db_table = "product_groups"
        verbose_name = "Базовый товар (без цвета)"
        verbose_name_plural = "Базовые товары"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ProductGroupCategory(models.Model):
    """
    Модель связи группы товаров и категории
    """

    group = models.ForeignKey(
        ProductGroup,
        on_delete=models.CASCADE,
        related_name="group_categories",
        verbose_name="Группа товаров",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="category_groups",
        verbose_name="Категория",
    )

    class Meta:
        db_table = "product_group_categories"
        verbose_name = "Категория группы товаров"
        verbose_name_plural = "Категории групп товаров"
        unique_together = ("group", "category")
        indexes = [
            models.Index(fields=["group", "category"]),
        ]

    def __str__(self):
        return f"{self.group.name} - {self.category.name}"


class Product(models.Model):
    """
    Модель товара (конкретный цвет группы товаров)
    """

    group = models.ForeignKey(
        ProductGroup,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="Базовый товар",
        help_text="Выберите товар из списка",
    )
    color = models.ForeignKey(
        Color,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="Цвет товара",
        help_text="Выберите цвет",
    )
    name = models.CharField(
        max_length=250,
        verbose_name="Полное название",
        help_text="Например: PUFFER JACKET gen 2 washed black",
    )
    slug = models.SlugField(
        unique=True,
        blank=True,
        verbose_name="URL (латиницей)",
        help_text="Будет сгенерирован автоматически из названия",
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Базовая цена",
        help_text="Цена для всех размеров, если не указана индивидуальная",
    )
    is_active = models.BooleanField(default=False, verbose_name="Показывать на сайте")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        db_table = "products"
        verbose_name = "Товар в продаже (с цветом)"
        verbose_name_plural = "Товары в продаже"
        ordering = ["name"]
        unique_together = ("group", "color")
        indexes = [
            models.Index(fields=["group", "color"]),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        if self.group_id and self.color_id:
            exists = (
                Product.objects.filter(group=self.group, color=self.color)
                .exclude(pk=self.pk)
                .exists()
            )
            if exists:
                raise ValidationError(
                    f"Товар '{self.group.name}' с цветом '{self.color.name}' уже существует."
                )


class ProductVariant(models.Model):
    """
    Модель варианта товара (размер)
    """

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="variants", verbose_name="Товар"
    )
    size = models.ForeignKey(
        Size,
        on_delete=models.PROTECT,
        related_name="variants",
        verbose_name="Размер",
        help_text="Выберите размер из списка",
    )
    sku = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Артикул",
        blank=True,
        help_text="Будет сгенерирован автоматически",
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена для этого размера",
        null=True,
        blank=True,
        help_text="Оставьте пустым, если цена такая же как у товара",
    )
    stock = models.PositiveIntegerField(default=0, verbose_name="Количество на складе")
    is_active = models.BooleanField(default=True, verbose_name="Доступен для заказа")
    weight = models.PositiveIntegerField(
        default=500,
        verbose_name="Вес (грамм)",
        help_text="Вес одной единицы товара в граммах",
    )
    dimension_length = models.PositiveIntegerField(
        default=30,
        verbose_name="Длина (см)",
        help_text="Длина упаковки в сантиметрах",
    )
    dimension_width = models.PositiveIntegerField(
        default=20,
        verbose_name="Ширина (см)",
        help_text="Ширина упаковки в сантиметрах",
    )
    dimension_height = models.PositiveIntegerField(
        default=10,
        verbose_name="Высота (см)",
        help_text="Высота упаковки в сантиметрах",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        db_table = "product_variants"
        verbose_name = "Размер и остаток"
        verbose_name_plural = "Размеры и остатки"
        ordering = ["size"]
        unique_together = ("product", "size")
        indexes = [
            models.Index(fields=["product", "size"]),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.size.name}"

    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = slugify(f"{self.product.slug}-{self.size.name}")
        super().save(*args, **kwargs)

    def get_price(self):
        """Возвращает цену варианта или базовую цену товара"""
        return self.price if self.price is not None else self.product.price


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
        verbose_name = "Фотография товара"
        verbose_name_plural = "Фотографии и медиа"
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
