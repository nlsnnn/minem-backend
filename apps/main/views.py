from rest_framework import generics, permissions


from .models import Category, Product
from .serializers import (
    CategorySerializer,
    ProductListSerializer,
    ProductDetailSerializer,
)


class CategoryListView(generics.ListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.filter(is_active=True).order_by("name")
    permission_classes = [permissions.AllowAny]


class CategoryProductListView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        category_slug = self.kwargs.get("slug")
        return (
            Product.objects.filter(
                group__categories__slug=category_slug, is_active=True
            )
            .select_related("group", "color")
            .prefetch_related("media", "variants")
        )


class ProductListView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    queryset = (
        Product.objects.filter(is_active=True)
        .select_related("group", "color")
        .prefetch_related("media", "variants")
    )
    ordering_fields = ["created_at", "name", "id", "price"]
    ordering = ["-created_at"]
    permission_classes = [permissions.AllowAny]


class ProductDetailView(generics.RetrieveAPIView):
    serializer_class = ProductDetailSerializer
    queryset = (
        Product.objects.filter(is_active=True)
        .select_related("group", "color")
        .prefetch_related(
            "media",
            "variants",
            "group__products__color",
            "group__products__media",
            "group__products__variants",
            "group__categories",
        )
    )
    lookup_field = "slug"
    permission_classes = [permissions.AllowAny]
