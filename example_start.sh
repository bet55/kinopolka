#!/bin/bash

export ENVIRONMENT=${ENVIRONMENT:-dev}

# kinopoisk
export KP_API_TOKEN=""

# django
export DEBUG="1"
export ALLOWED_HOSTS="0.0.0.0;127.0.0.1;localhost;192.168.0.15;xn--80apfbelhai.xn--p1ai,kinopolka.com"
export SECRET_KEY=""

#email
export EMAIL_HOST_USER=''
export EMAIL_HOST_PASSWORD=''

# telegram
export TELEGRAM_BOT_TOKEN=""
export TELEGRAM_GROUP_ID=""

# logs
export LOKI_URL='http://localhost:3100'
export APP_NAME='kinopolka'
export SERVICE_NAME='django'

# Заменим переменные, если на проде
if [ "$ENVIRONMENT" = "prod" ]; then
  export DEBUG="0"
  export ALLOWED_HOSTS="xn--80apfbelhai.xn--p1ai,kinopolka.com"
  export LOKI_URL=""
  export TELEGRAM_GROUP_ID=""
  export SSL_REDIRECT='True'
fi

# start
uv run utils/top_secret.py
echo "== Starting in $ENVIRONMENT mode =="
#uv run manage.py runserver 0.0.0.0:8000
uv run uvicorn filmoclub.asgi:application --host 0.0.0.0 --port 8000
