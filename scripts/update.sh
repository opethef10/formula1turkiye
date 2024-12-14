#! /usr/bin/env bash
set -e

# Check if the script is running inside a virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Error: This script must be run inside a virtual environment." >&2
    exit 1
fi

scripts/copydb.py
git pull
pip install -r requirements/production.txt
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py test --settings=f1t.settings.tests
scripts/reload.sh
