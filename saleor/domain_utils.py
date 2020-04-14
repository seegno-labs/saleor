import os
import sys
import json
import dj_database_url

from functools import wraps
from urllib import request, parse
from django.conf import settings
from django.db import connections, transaction
from threadlocals.threadlocals import get_current_request

saas_manager_host = os.environ.get('SAAS_MANAGER_HOST')
user_manager_host = os.environ.get('USER_MANAGER_HOST')
services_protocol = os.environ.get('SERVICES_PROTOCOL') or 'http'

def get_domain():
    opts = sys.argv
    request = get_current_request()

    if request is not None:
        return request.headers["X-Domain-ID"]
    if "--domain" in opts:
        index = opts.index("--domain") + 1
        return opts[index]

def update_migration_state(domain=None, state=None):
    try:
        payload = {'ecommerceStatus': state}
        url = f"{services_protocol}://{saas_manager_host}/domains/{domain}"
        data = parse.urlencode(payload).encode()
        req = request.Request(url, data=data)
        req.get_method = lambda: "PATCH"

        with request.urlopen(req) as response:
            resp = response.read().decode('utf-8')
            return json.loads(resp)
    except Exception as e:
        raise e

def update_ecommerce_id(domain_id=None, user_id=None, saleor_id=None):
    try:
        payload = {'ecommerceId': saleor_id}
        url = f"{services_protocol}://{user_manager_host}/users/{user_id}"
        data = parse.urlencode(payload).encode()
        headers = { "X-Domain-ID": domain_id }
        req = request.Request(url, headers=headers, data=data)
        req.get_method = lambda: "PATCH"

        with request.urlopen(req) as response:
            resp = response.read().decode('utf-8')
            return json.loads(resp)
    except Exception as e:
        raise e

def fetch_credentials(domain=None):
    try:
        url = f"{services_protocol}://{saas_manager_host}/domains/{domain}/database"
        req = request.Request(url, data=None)

        with request.urlopen(req) as response:
            credentials = response.read().decode('utf-8')
            return json.loads(credentials)
    except Exception as e:
        raise e

def serialize_connection(credentials):
    client = credentials.get("client")
    connection = credentials.get("connection")
    host = connection.get("host")
    port = connection.get("port")
    user = connection.get("user")
    password = connection.get("password")
    database = connection.get("database")

    return f"{client}://{user}:{password}@{host}:{port}/{database}"

def setup_celery_connection(domain):
    credentials = fetch_credentials(domain)
    connection_string = serialize_connection(credentials)
    connections.databases[domain] = dj_database_url.parse(connection_string)
    settings.DOMAIN["celery"] = domain

def transaction_domain_atomic(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        domain = get_domain()

        with transaction.atomic(using=domain):
            return fn(*args, **kwargs)

    return wrapper

def add_saleor_schema(domain):
    with connections[domain].cursor() as cursor:
        try:
            cursor.execute('CREATE SCHEMA IF NOT EXISTS saleor')
        finally:
            cursor.close()
