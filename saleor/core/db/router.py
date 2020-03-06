import sys
import dj_database_url
from django.conf import settings
from django.db import connections
from threadlocals.threadlocals import get_current_request
from ...domain_utils import fetch_credentials, serialize_connection

class DatabaseRouter:
    def _default_db(self):
        domain = None
        db_conn = None

        # this check is for running tasks on celery
        # celery tasks spawn different workers/processes
        # and there's no request object on their context
        if "celery" in settings.DOMAIN:
            return settings.DOMAIN["celery"]

        # this check handles populatedb commands
        elif "--database" in sys.argv and "--domain" in sys.argv:
            db_index = sys.argv.index("--database") + 1
            domain_index = sys.argv.index("--domain") + 1

            db_conn = sys.argv[db_index]
            domain = sys.argv[domain_index]

        # handles any HTTP request
        else:
            request = get_current_request()

            if request is not None and "X-Domain-ID" in request.headers:
                domain = request.headers["X-Domain-ID"]
                credentials = fetch_credentials(domain)
                db_conn = serialize_connection(credentials)

        if db_conn is not None and domain is not None:
            connections.databases[domain] = dj_database_url.parse(db_conn)
            connections.databases[domain]["OPTIONS"] = { "options": "-c search_path=saleor" }

        return domain

    def db_for_read(self, model, **hints):
        return self._default_db()

    def db_for_write(self, model, **hints):
        return self._default_db()

    def allow_relation(self, obj1, obj2, **hints):
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return True
