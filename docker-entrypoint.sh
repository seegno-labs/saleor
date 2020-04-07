#!/bin/bash

python3 manage.py collectstatic --no-input

echo "CONTAINER_JOB=$CONTAINER_JOB"

if [ $CONTAINER_JOB == "SALEOR" ]
then
  echo "Running Saleor server..."
  python manage.py runserver 0.0.0.0:$PORT
elif [ $CONTAINER_JOB == "CELERY" ]
then
  echo "Running celery..."
  celery -A saleor worker --app=saleor.celeryconf:app --loglevel=info
fi

exec "$@"
