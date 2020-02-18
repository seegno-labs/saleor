import json
from django.http import HttpResponse, JsonResponse

from .tasks import run_migrations

def migrate(request):
    if not request.body:
        error = { "error": "Missing request body" }
        return JsonResponse(error, status=400)

    body = json.loads(request.body)
    users = body.get('users', [])

    run_migrations.delay(users=users)

    return HttpResponse(status=204)
