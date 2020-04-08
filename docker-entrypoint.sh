#!/bin/bash

python3 manage.py collectstatic --no-input

if [ $CONTAINER_JOB == "saleor" ]
then
  echo "Starting Saleor server..."
  python manage.py runserver 0.0.0.0:$PORT
elif [ $CONTAINER_JOB == "celery" ]
then
  echo "Starting Celery..."
  celery -A saleor worker --app=saleor.celeryconf:app --loglevel=${CELERY_DEBUG:-info}
fi

exec "$@"
