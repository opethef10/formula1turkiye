#! /bin/bash
python manage.py runserver
sleep 5
python -m webbrowser http://localhost:8000 
