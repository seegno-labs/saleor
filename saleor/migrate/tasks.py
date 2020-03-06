import dj_database_url

from celery import Task, signals
from django.db import connections
from django.conf import settings
from django.utils.text import slugify
from django.core.management import call_command
from faker import Factory
from prices import Money

from ..account.models import Address, User
from ..celeryconf import app
from ..domain_task import DomainTask
from ..domain_utils import (
    update_ecommerce_id,
    update_migration_state,
    setup_celery_connection
)
from ..shipping.models import ShippingMethod, ShippingMethodType, ShippingZone
from ..warehouse.models import Stock, Warehouse
from .utils import countries

fake = Factory.create()

def create_users(domain, users):
    for user in users:
        try:
            saleor_user = User.objects.create_user(
                first_name=user.get('name'),
                last_name="",
                email=user.get('email'),
                password="password",
                is_active=True,
                is_staff=user.get('isSuperuser', False),
                is_superuser=user.get('isSuperuser', False)
            )

            update_ecommerce_id(domain, user.get('id'), saleor_user.id)

        except Exception as e:
            raise e

def create_fake_address():
    address = Address(
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        street_address_1=fake.street_address(),
        city=fake.city(),
        country="US"
    )

    if address.country == "US":
        state = fake.state_abbr()
        address.country_area = state
        address.postal_code = fake.postalcode_in_state(state)
    else:
        address.postal_code = fake.postalcode()

    address.save()
    return address


def setup_warehouse():
    shipping_zone_name = "Default"
    shipping_zone = ShippingZone.objects.get_or_create(
        name=shipping_zone_name,
        countries=countries,
        default=True
    )[0]

    ShippingMethod.objects.create(
        name="Default Method",
        price=Money(0, settings.DEFAULT_CURRENCY),
        shipping_zone=shipping_zone,
        type=ShippingMethodType.WEIGHT_BASED,
        minimum_order_price=Money(0, settings.DEFAULT_CURRENCY),
        maximum_order_price_amount=None,
        minimum_order_weight=0,
        maximum_order_weight=None,
    )

    warehouse, _ = Warehouse.objects.update_or_create(
        name=shipping_zone_name,
        slug=slugify(shipping_zone_name),
        company_name=fake.company(),
        address=create_fake_address()
    )

    warehouse.shipping_zones.add(shipping_zone)

@signals.task_postrun.connect
def handle_post_migration(signal=None, sender=None, task_id=None, task=None, *args, **kwargs):
    if task.name == "saleor.migrate.tasks.run_migrations":
        users = kwargs.get('kwargs').get('users')
        domain = kwargs.get('kwargs').get('domain')

        if len(users):
            setup_warehouse()
            create_users(domain, users)

        update_migration_state(domain, "ready")

@app.task(base=DomainTask)
def run_migrations(**kwargs):
    users = kwargs.get('users')
    domain = kwargs.get('domain')

    setup_celery_connection(domain)
    call_command("migrate", database=domain)
