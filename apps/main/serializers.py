from rest_framework import serializers
from django.utils.text import slugify

from .models import (
    Category,
    Product,
    ProductVariant,
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]

    def create(self, validated_data):
        validated_data["slug"] = slugify(validated_data["name"])
        return super().create(validated_data)


class ProductListSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    prices = serializers.SerializerMethodField()
    media = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "excerpt",
            "categories",
            "prices",
            "media",
        ]

    def get_prices(self, obj: Product):
        variants = obj.variants.filter(is_active=True)
        if not variants.exists():
            return None

        prices = set(variants.values_list("price", flat=True))
        return prices

    def get_media(self, obj: Product):
        media_qs = obj.media.filter().order_by("position").all()
        main_media = media_qs.filter(is_main=True).first()
        media = (
            [main_media] + [m for m in media_qs if m != main_media]
            if main_media
            else media_qs
        )

        return [m.url for m in media]


class ProductVariantDetailSerializer(serializers.ModelSerializer):
    media = serializers.SerializerMethodField()
    options = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariant
        fields = [
            "id",
            "sku",
            "price",
            "options",
            "media",
            "is_active",
            "created_at",
            "updated_at",
        ]

    def get_options(self, obj):
        option_values = obj.option_values.select_related("option_value").all()
        return {
            ov.option_value.option.name: ov.option_value.value for ov in option_values
        }

    def get_media(self, obj):
        media_qs = (
            obj.product.media.filter(variant_id=obj.id).order_by("position").all()
        )
        main_media = media_qs.filter(is_main=True).first()
        media = (
            [main_media] + [m for m in media_qs if m != main_media]
            if main_media
            else media_qs
        )

        return [m.url for m in media]


class ProductDetailSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    media = serializers.SerializerMethodField()
    variants = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "excerpt",
            "description",
            "categories",
            "media",
            "variants",
        ]

    def get_media(self, obj: Product):
        media_qs = obj.media.filter().order_by("position").all()
        main_media = media_qs.filter(is_main=True).first()
        media = (
            [main_media] + [m for m in media_qs if m != main_media]
            if main_media
            else media_qs
        )

        return [m.url for m in media]

    def get_variants(self, obj: Product):
        variants = obj.variants.filter(is_active=True)
        serializer = ProductVariantDetailSerializer(variants, many=True)
        return serializer.data
