#!/bin/sh

export KP_API_TOKEN=""
export DEBUG="1"
export SECRET_KEY=""

python utils/top_secret.py
python manage.py runserver 0.0.0.0:8000