#!/bin/sh

# kinopoisk
export KP_API_TOKEN=

# django
export DEBUG="0"
export SECRET_KEY=

#email
export EMAIL_HOST_USER=
export EMAIL_HOST_PASSWORD=

# telegram
export TELEGRAM_BOT_TOKEN=
export TELEGRAM_GROUP_ID=

# logs
#export LOKI_URL='http://loki:3100' #dev
export LOKI_URL='http://localhost:3100' #prod
export APP_NAME='kinopolka'
export SERVICE_NAME='django'

# start
uv run utils/top_secret.py
#uv run manage.py runserver --insecure 0.0.0.0:8000 # если нужно тестить debug mod
#uv run manage.py runserver 0.0.0.0:8000 # prod
uv run uvicorn filmoclub.asgi:application --host 0.0.0.0 --port 8000 # uvicorn