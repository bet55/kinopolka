#!/bin/bash
# Шаблон env.sh: скопируй в env.sh (`cp example_env.sh env.sh`) и заполни значения.
# env.sh лежит в .gitignore — секреты в git не попадают.
# Разовые management-команды: `source env.sh` в терминале, дальше uv run manage.py <команда>.

export ENVIRONMENT=${ENVIRONMENT:-dev}

# kinopoisk
export KP_API_TOKEN=""

# django
export DEBUG="1"
export ALLOWED_HOSTS="0.0.0.0;127.0.0.1;localhost;192.168.0.15;xn--80apfbelhai.xn--p1ai;kinopolka.com"
export SECRET_KEY=""
# Код «свой-чужой» для изменяющих запросов (только ASCII). Пустой — проверка выключена.
export TEA_CODE=""

# Суперпользователь админки /boss/ (создаётся при старте; пустой логин — шаг пропускается)
export DJANGO_SUPERUSER_USERNAME=""
export DJANGO_SUPERUSER_PASSWORD=""

# Порт приложения (для локальной разработки; в докере пробрасывается 8000)
export APP_PORT="8011"

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
  export ALLOWED_HOSTS="xn--80apfbelhai.xn--p1ai;kinopolka.com"
  export LOKI_URL=""
  export TELEGRAM_GROUP_ID=""
  export SSL_REDIRECT='True'
  export APP_PORT="8000"
fi
