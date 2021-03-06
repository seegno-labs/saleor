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
    add_saleor_schema,
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
        id = user.get('id')
        email = user.get('email')
        name = user.get('email')
        roles = user.get('roles')
        is_superuser = 'owner' in roles

        try:
            saleor_user = User.objects.create_user(
                first_name=name,
                last_name="",
                email=email,
                password="password",
                is_active=True,
                is_staff=is_superuser,
                is_superuser=is_superuser
            )

            update_ecommerce_id(domain, id, saleor_user.id)

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
    warehouses = Warehouse.objects.all()
    has_warehouse = warehouses.count() > 0

    if not has_warehouse:
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

@signals.task_success.connect
def handle_migrate_success(result, *args, **kwargs):
    task = kwargs.get('sender').name

    if task == 'saleor.migrate.tasks.run_migrations':
        users = result.get('users')
        domain = result.get('domain')

        setup_warehouse()

        if len(users):
            create_users(domain, users)

        update_migration_state(domain, "ready")

@signals.task_failure.connect
def handle_migrate_failure(task_id, exception, traceback, einfo, *args, **kwargs):
    task = kwargs.get('sender').name
    domain = kwargs.get('kwargs').get('domain')

    if task == 'saleor.migrate.tasks.run_migrations':
        update_migration_state(domain, "failed")

@app.task(base=DomainTask)
def run_migrations(**kwargs):
    users = kwargs.get('users')
    domain = kwargs.get('domain')

    setup_celery_connection(domain)
    add_saleor_schema(domain)
    update_migration_state(domain, "preparing")
    call_command("migrate", database=domain)

    return {
        'domain': domain,
        'users': users
    }
