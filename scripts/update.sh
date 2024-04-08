#! /usr/bin/env bash
set -e

git pull
pip install -r requirements/production.txt
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py test --settings=f1t.settings.tests
scripts/reload.sh

