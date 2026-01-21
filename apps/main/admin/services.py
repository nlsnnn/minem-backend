from itertools import product as itertools_product
from collections import defaultdict
from ..models import ProductVariant, VariantOptionValue, ProductMedia


def generate_sku(product_slug, option_values):
    """Генерирует SKU по единому шаблону: slug-OPT1-OPT2"""
    option_codes = "-".join(sorted(ov.value for ov in option_values))
    return f"{product_slug}-{option_codes}".upper()


def generate_product_variants(
    product, option_values, base_price, stock, is_active, copy_media=False
):
    """
    Генерирует варианты товара из выбранных значений опций.
    Группирует значения по опциям и создает все возможные комбинации.
    """
    options_map = defaultdict(list)
    for ov in option_values:
        options_map[ov.option].append(ov)

    if len(options_map) < 1:
        return 0, 0

    combinations = list(itertools_product(*options_map.values()))
    created_count = 0
    skipped_count = 0
    product_media = (
        list(product.media.filter(variant__isnull=True)) if copy_media else []
    )

    for combination in combinations:
        sku = generate_sku(product.slug, combination)

        if ProductVariant.objects.filter(sku=sku).exists():
            skipped_count += 1
            continue

        variant = ProductVariant.objects.create(
            product=product, sku=sku, price=base_price, stock=stock, is_active=is_active
        )

        for option_value in combination:
            VariantOptionValue.objects.create(
                variant=variant, option_value=option_value
            )

        for media in product_media:
            ProductMedia.objects.create(
                product=product,
                variant=variant,
                type=media.type,
                url=media.url,
                position=media.position,
                is_main=False,
            )

        created_count += 1

    return created_count, skipped_count
