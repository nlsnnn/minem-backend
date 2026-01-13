from django.urls import path
from . import views


urlpatterns = [
    # Categories
    path("categories/", views.CategoryListView.as_view(), name="category-list"),
    path(
        "categories/<slug:slug>/",
        views.CategoryProductListView.as_view(),
        name="category-product-list",
    ),
    
    # Products
    path("", views.ProductListView.as_view(), name="product-list"),
    path("<slug:slug>/", views.ProductDetailView.as_view(), name="product-detail"),
]
