from config.admin import admin_site
from .color import ColorAdmin
from .size import SizeAdmin
from .product import CategoryAdmin, ProductAdmin, ProductGroupAdmin
from .variant import ProductVariantAdmin
from .media import ProductMediaAdmin
from ..models import (
    Color,
    Size,
    Category,
    ProductGroup,
    Product,
    ProductVariant,
    ProductMedia,
)

admin_site.register(Color, ColorAdmin)
admin_site.register(Size, SizeAdmin)
admin_site.register(Category, CategoryAdmin)
admin_site.register(ProductGroup, ProductGroupAdmin)
admin_site.register(Product, ProductAdmin)
admin_site.register(ProductVariant, ProductVariantAdmin)
admin_site.register(ProductMedia, ProductMediaAdmin)

__all__ = [
    "ColorAdmin",
    "SizeAdmin",
    "CategoryAdmin",
    "ProductAdmin",
    "ProductGroupAdmin",
    "ProductVariantAdmin",
    "ProductMediaAdmin",
]
