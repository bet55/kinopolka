#!/usr/bin/env bash
#
# Скачивает с VPS системные конфиги (nginx, ufw, fail2ban) в локальную папку-бэкап.
# При каждом запуске тянет свежие версии (перезаписывает локальные).
#
set -euo pipefail

# ============ НАСТРОЙКИ ============
# Куда складывать бэкап конфигов. Меняй при необходимости.
DEST_DIR="/home/stephan/projects/vps_db/settings_files"

# Параметры удалённого сервера.
REMOTE_USER="root"
REMOTE_HOST="109.120.159.182"
REMOTE_PORT="3988"
# ===================================

REMOTE="${REMOTE_USER}@${REMOTE_HOST}"
SSH_CMD="ssh -p ${REMOTE_PORT}"

# Конфиги на сервере (абсолютные пути). Все складываются плоско в DEST_DIR.
REMOTE_FILES=(
    "/etc/nginx/sites-available/django_project"
    "/etc/ufw/before.rules"
    "/etc/ufw/user.rules"
    "/etc/fail2ban/jail.local"
)

echo "Конфиги VPS будут сохранены в:"
echo "    ${DEST_DIR}"
echo "С сервера: ${REMOTE}  (порт ${REMOTE_PORT})"
echo "Существующие файлы будут перезаписаны свежими версиями."
echo
read -r -p "Начать загрузку? [y/N] " answer
case "${answer}" in
    [yY] | [yY][eE][sS]) ;;
    *)
        echo "Отменено."
        exit 0
        ;;
esac

mkdir -p "${DEST_DIR}"

# -avh атрибуты/подробно/по-человечески, --progress прогресс.
# Без --ignore-existing: всегда тянем актуальную версию.
RSYNC_OPTS=(-avh --progress -e "${SSH_CMD}")

for f in "${REMOTE_FILES[@]}"; do
    echo
    echo ">>> ${f}"
    rsync "${RSYNC_OPTS[@]}" "${REMOTE}:${f}" "${DEST_DIR}/"
done

echo
echo "Готово. Сохранено файлов: ${#REMOTE_FILES[@]}"
