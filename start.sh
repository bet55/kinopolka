#!/bin/bash
# Логика запуска приложения. Секретов здесь нет — все переменные окружения
# лежат в env.sh (вне git, шаблон — example_env.sh).

# Втягиваем окружение. Именно «.», а не «source»: в докере скрипт
# запускается через sh (dash), который слова source не знает.
if [ ! -f ./env.sh ]; then
  echo "Не найден env.sh! Скопируй example_env.sh в env.sh и заполни значения."
  exit 1
fi
. ./env.sh

# Собираем статику
echo "== Collecting static files =="
uv run manage.py collectstatic --noinput

# Суперпользователь для админки /boss/. Если уже существует —
# createsuperuser вернёт ошибку, гасим её и едем дальше
if [ -n "$DJANGO_SUPERUSER_USERNAME" ]; then
  echo "== Creating superuser =="
  uv run manage.py createsuperuser --noinput --email "" 2>/dev/null \
    || echo "== Superuser already exists =="
fi

# start
uv run utils/top_secret.py
echo "== Starting in $ENVIRONMENT mode on port ${APP_PORT:-8000} =="

# В prod --reload не нужен: файловый вотчер зря ест ресурсы и перезапускает
# приложение при любом изменении файлов (например, при заливке открытки)
if [ "$ENVIRONMENT" = "prod" ]; then
  uv run uvicorn filmoclub.asgi:application --host 0.0.0.0 --port "${APP_PORT:-8000}" --log-level warning
else
  uv run uvicorn filmoclub.asgi:application --host 0.0.0.0 --port "${APP_PORT:-8000}" --reload
fi
