from celery import Task
from .domain_utils import get_domain, fetch_currency

class DomainTask(Task):
    abstract = True

    def apply_async(self, args=None, kwargs=None, **rest):
        self._include_request_context(kwargs)
        return super(DomainTask, self).apply_async(args, kwargs, **rest)

    def apply(self, args=None, kwargs=None, **rest):
        self._include_request_context(kwargs)
        return super(DomainTask, self).apply(args, kwargs, **rest)

    def retry(self, args=None, kwargs=None, **rest):
        self._include_request_context(kwargs)
        return super(DomainTask, self).retry(args, kwargs, **rest)

    def _include_request_context(self, kwargs):
        domain = get_domain()
        currency = fetch_currency(domain)
        kwargs["domain"] = domain
        kwargs["currency"] = currency
