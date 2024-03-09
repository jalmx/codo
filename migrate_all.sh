#! /bin/bash

source venv/bin/activate && python manage.py makemigrations && python manage.py migrate && python manage.py makemigrations codo_app && python manage.py migrate codo_app

echo "==============>  Now run server :)"