from typing import Iterable, List, Optional

from ..celeryconf import app
from ..discount.models import Sale
from .models import Attribute, Product, ProductType, ProductVariant
from .utils.attributes import generate_name_for_variant
from .utils.variant_prices import (
    update_product_minimal_variant_price,
    update_products_minimal_variant_prices,
    update_products_minimal_variant_prices_of_catalogues,
    update_products_minimal_variant_prices_of_discount,
)

from ..domain_task import DomainTask
from ..domain_utils import setup_celery_connection

def _update_variants_names(instance: ProductType, saved_attributes: Iterable):
    """Product variant names are created from names of assigned attributes.

    After change in attribute value name, for all product variants using this
    attributes we need to update the names.
    """
    initial_attributes = set(instance.variant_attributes.all())
    attributes_changed = initial_attributes.intersection(saved_attributes)
    if not attributes_changed:
        return
    variants_to_be_updated = ProductVariant.objects.filter(
        product__in=instance.products.all(),
        product__product_type__variant_attributes__in=attributes_changed,
    )
    variants_to_be_updated = variants_to_be_updated.prefetch_related(
        "attributes__values__translations"
    ).all()
    for variant in variants_to_be_updated:
        variant.name = generate_name_for_variant(variant)
        variant.save(update_fields=["name"])


@app.task(base=DomainTask)
def update_variants_names(product_type_pk: int, saved_attributes_ids: List[int], **kwargs):
    domain = kwargs.get('domain')

    setup_celery_connection(domain)

    instance = ProductType.objects.get(pk=product_type_pk)
    saved_attributes = Attribute.objects.filter(pk__in=saved_attributes_ids)
    _update_variants_names(instance, saved_attributes)


@app.task(base=DomainTask)
def update_product_minimal_variant_price_task(product_pk: int, **kwargs):
    domain = kwargs.get('domain')

    setup_celery_connection(domain)

    product = Product.objects.get(pk=product_pk)
    update_product_minimal_variant_price(product)


@app.task(base=DomainTask)
def update_products_minimal_variant_prices_of_catalogues_task(
    product_ids: Optional[List[int]] = None,
    category_ids: Optional[List[int]] = None,
    collection_ids: Optional[List[int]] = None,
    **kwargs
):
    domain = kwargs.get('domain')

    setup_celery_connection(domain)

    update_products_minimal_variant_prices_of_catalogues(
        product_ids, category_ids, collection_ids
    )


@app.task(base=DomainTask)
def update_products_minimal_variant_prices_of_discount_task(discount_pk: int, **kwargs):
    domain = kwargs.get('domain')

    setup_celery_connection(domain)

    discount = Sale.objects.get(pk=discount_pk)
    update_products_minimal_variant_prices_of_discount(discount)


@app.task(base=DomainTask)
def update_products_minimal_variant_prices_task(product_ids: List[int], **kwargs):
    domain = kwargs.get('domain')

    setup_celery_connection(domain)

    products = Product.objects.filter(pk__in=product_ids)
    update_products_minimal_variant_prices(products)
