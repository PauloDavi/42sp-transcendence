#!/bin/sh

python manage.py makemigrations --noinput
python manage.py migrate --noinput
python manage.py compilemessages
python manage.py makemessages -l pt_BR -l en -l es
python manage.py collectstatic --noinput
python manage.py shell < ./create_superuser.py || true

exec "$@"
