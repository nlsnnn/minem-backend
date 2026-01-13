from rest_framework import generics, filters, pagination, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response


from .models import Category, Product
from .serializers import (
    CategorySerializer,
    ProductListSerializer,
    ProductDetailSerializer,
)


class CategoryListView(generics.ListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all().order_by("name")
    permission_classes = [permissions.AllowAny]


class CategoryProductListView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        category_slug = self.kwargs.get("slug")
        return Product.objects.filter(categories__slug=category_slug).prefetch_related(
            "categories", "media", "variants"
        )


class ProductListView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    queryset = Product.objects.all().prefetch_related("categories", "media", "variants")
    ordering_fields = ["created_at", "name", "id"]
    ordering = ["-created_at"]
    permission_classes = [permissions.AllowAny]


class ProductDetailView(generics.RetrieveAPIView):
    serializer_class = ProductDetailSerializer
    queryset = Product.objects.all().prefetch_related(
        "categories",
        "media",
        "variants__option_values__option_value",
        "contents",
    )
    lookup_field = "slug"
    permission_classes = [permissions.AllowAny]
