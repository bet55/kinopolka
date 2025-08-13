#!/bin/sh

# kinopoisk
export KP_API_TOKEN=""

# django
export DEBUG="1"
export SECRET_KEY="django-insecure-moq19!=-t5w#&p!h4aw=b4hzs9k8^290t513qhm-86r39=4&#y"
export ALLOWED_HOSTS="0.0.0.0;127.0.0.1;localhost;192.168.0.15;xn--80apfbelhai.xn--p1ai,kinopolka.com"

#email
export EMAIL_HOST_USER=''
export EMAIL_HOST_PASSWORD=''

# telegram
export TELEGRAM_BOT_TOKEN=""
export TELEGRAM_GROUP_ID=""


# logs
export LOKI_URL='http://loki:3100' #prod
export APP_NAME='kinopolka'
export SERVICE_NAME='django'

# start
uv run utils/top_secret.py
uv run manage.py runserver 0.0.0.0:8000
#uv run uvicorn filmoclub.asgi:application --host 0.0.0.0 --port 8000