from rest_framework import serializers
from django.utils.text import slugify

from .models import (
    Category,
    Color,
    ProductGroup,
    Product,
    ProductVariant,
)


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ["id", "name", "slug"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]

    def create(self, validated_data):
        validated_data["slug"] = slugify(validated_data["name"])
        return super().create(validated_data)


class ProductGroupBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductGroup
        fields = ["id", "name", "slug"]


class ProductVariantSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    size = serializers.CharField(source="size.name")

    class Meta:
        model = ProductVariant
        fields = ["id", "size", "sku", "price", "stock", "is_active"]

    def get_price(self, obj):
        return obj.get_price()


class ProductListSerializer(serializers.ModelSerializer):
    group = ProductGroupBriefSerializer(read_only=True)
    color = ColorSerializer(read_only=True)
    images = serializers.SerializerMethodField()
    available_sizes = serializers.SerializerMethodField()
    in_stock = serializers.SerializerMethodField()
    excerpt = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "group",
            "color",
            "price",
            "images",
            "available_sizes",
            "in_stock",
            "excerpt",
        ]

    def get_images(self, obj):
        media_qs = obj.media.all().order_by("-is_main", "position")
        return [m.url for m in media_qs]

    def get_available_sizes(self, obj):
        return list(
            obj.variants.filter(is_active=True, stock__gt=0)
            .select_related("size")
            .values_list("size__name", flat=True)
            .distinct()
        )

    def get_in_stock(self, obj):
        return obj.variants.filter(is_active=True, stock__gt=0).exists()

    def get_excerpt(self, obj):
        return obj.group.excerpt if obj.group else ""


class RelatedColorSerializer(serializers.ModelSerializer):
    color = ColorSerializer(read_only=True)
    images = serializers.SerializerMethodField()
    in_stock = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ["id", "name", "slug", "color", "price", "images", "in_stock"]

    def get_images(self, obj):
        media_qs = obj.media.all().order_by("-is_main", "position")
        return [m.url for m in media_qs]

    def get_in_stock(self, obj):
        return obj.variants.filter(is_active=True, stock__gt=0).exists()


class ProductDetailSerializer(serializers.ModelSerializer):
    group = serializers.SerializerMethodField()
    color = ColorSerializer(read_only=True)
    media = serializers.SerializerMethodField()
    variants = ProductVariantSerializer(many=True, read_only=True)
    related_colors = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "group",
            "color",
            "price",
            "media",
            "variants",
            "related_colors",
            "categories",
        ]

    def get_group(self, obj):
        if not obj.group:
            return None
        return {
            "id": obj.group.id,
            "name": obj.group.name,
            "slug": obj.group.slug,
            "description": obj.group.description,
            "excerpt": obj.group.excerpt,
            "materials": obj.group.materials,
            "care_instructions": obj.group.care_instructions,
            "size_chart": obj.group.size_chart,
            "delivery_info": obj.group.delivery_info,
        }

    def get_media(self, obj):
        media_qs = obj.media.all().order_by("position")
        return [
            {"url": m.url, "type": m.type, "position": m.position} for m in media_qs
        ]

    def get_related_colors(self, obj):
        if not obj.group:
            return []
        related_products = (
            obj.group.products.exclude(id=obj.id)
            .filter(is_active=True)
            .select_related("color")
            .prefetch_related("media", "variants")
        )
        return RelatedColorSerializer(related_products, many=True).data

    def get_categories(self, obj):
        if not obj.group:
            return []
        categories = obj.group.categories.filter(is_active=True)
        return CategorySerializer(categories, many=True).data
