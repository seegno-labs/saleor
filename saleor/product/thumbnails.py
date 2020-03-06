from ..celeryconf import app
from ..core.utils import create_thumbnails
from ..domain_task import DomainTask
from ..domain_utils import setup_celery_connection
from .models import Category, Collection, ProductImage

@app.task(base=DomainTask)
def create_product_thumbnails(image_id: str, **kwargs):
    """Take a ProductImage model and create thumbnails for it."""
    domain = kwargs.get('domain')

    setup_celery_connection(domain)

    create_thumbnails(pk=image_id, model=ProductImage, size_set="products")


@app.task(base=DomainTask)
def create_category_background_image_thumbnails(category_id: str, **kwargs):
    """Take a Product model and create the background image thumbnails for it."""
    domain = kwargs.get('domain')

    setup_celery_connection(domain)

    create_thumbnails(
        pk=category_id,
        model=Category,
        size_set="background_images",
        image_attr="background_image",
    )


@app.task(base=DomainTask)
def create_collection_background_image_thumbnails(collection_id: str, **kwargs):
    """Take a Collection model and create the background image thumbnails for it."""
    domain = kwargs.get('domain')

    setup_celery_connection(domain)

    create_thumbnails(
        pk=collection_id,
        model=Collection,
        size_set="background_images",
        image_attr="background_image",
    )
