from itertools import product as itertools_product
from ..models import ProductVariant, VariantOptionValue, ProductMedia


def generate_sku(product_slug, option_values):
    """Генерирует SKU по единому шаблону: slug-OPT1-OPT2"""
    # chars = "aeiouy"

    option_codes = "-".join(ov.value for ov in option_values)

    return f"{product_slug}-{option_codes}".upper()


def generate_product_variants(
    product, options, base_price, stock, is_active, copy_media=False
):
    option_values_map = {opt: list(opt.values.all()) for opt in options}
    option_values_map = {k: v for k, v in option_values_map.items() if v}

    if not option_values_map:
        return 0, 0

    combinations = list(itertools_product(*option_values_map.values()))
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
