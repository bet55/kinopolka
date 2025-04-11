#!/bin/sh

# kinopoisk
export KP_API_TOKEN=

# django
export DEBUG="1"
export SECRET_KEY=

#email
export EMAIL_HOST_USER=
export EMAIL_HOST_PASSWORD=

# telegram
export TELEGRAM_BOT_TOKEN=
export TELEGRAM_GROUP_ID=

# logs
export LOKI_URL=
export APP_NAME='kinopolka'
export SERVICE_NAME='django'

# start
uv run utils/top_secret.py
uv run manage.py runserver 0.0.0.0:8000