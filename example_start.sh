#!/bin/sh

export KP_API_TOKEN=""
export DEBUG="1"
export SECRET_KEY=""

export EMAIL_HOST_USER=''
export EMAIL_HOST_PASSWORD=''

uv run utils/top_secret.py
uv run manage.py runserver 0.0.0.0:8000