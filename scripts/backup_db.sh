#!/usr/bin/env bash
#
# Ежедневный бэкап базы с VPS на локальную машину (запускается на ней).
# Дамп снимается через `sqlite3 .dump` — это консистентный SQL-слепок
# даже с живой базы (SQLite делает его внутри транзакции), поэтому
# просто копировать файл db.sqlite3 нельзя, а так — можно.
#
# Расписание — systemd-таймер пользователя (~/.config/systemd/user/
# kinopolka-backup.timer): ежедневно, с навёрстыванием пропущенных
# запусков (Persistent=true), если машина была выключена.
# Статус: systemctl --user list-timers kinopolka-backup.timer
set -euo pipefail

# ============ НАСТРОЙКИ ============
BACKUP_DIR="/home/stephan/projects/kinopolka_backup"
KEEP=7  # сколько последних дампов храним

# Параметры удалённого сервера.
REMOTE_USER="root"
REMOTE_HOST="109.120.159.182"
REMOTE_PORT="3988"
REMOTE_DB="/var/www/kinopolka/db.sqlite3"
# ===================================

mkdir -p "${BACKUP_DIR}"
target="${BACKUP_DIR}/db-$(date +%F).sql.gz"

# Дамп льётся сразу в gzip; сначала во временный файл, чтобы обрыв связи
# не оставил в папке битый «свежий» бэкап
ssh -p "${REMOTE_PORT}" -o BatchMode=yes "${REMOTE_USER}@${REMOTE_HOST}" \
    "sqlite3 ${REMOTE_DB} '.dump'" | gzip > "${target}.tmp"

# Дамп пустой базы или обрезанный ответ — не бэкап.
# zcat через stdin: по имени *.tmp (без .gz) он разжимать отказывается.
# grep -c, а не -q: -q обрывает чтение на первом совпадении, zcat ловит
# SIGPIPE, и pipefail считает это ошибкой пайплайна
tables=$(zcat < "${target}.tmp" | grep -c "CREATE TABLE" || true)
if [ "${tables}" -eq 0 ]; then
    rm -f "${target}.tmp"
    echo "Ошибка: в дампе нет ни одной таблицы, бэкап не сохранён" >&2
    exit 1
fi
mv "${target}.tmp" "${target}"

# Ротация: оставляем KEEP свежих, остальные удаляем
ls -1t "${BACKUP_DIR}"/db-*.sql.gz | tail -n +$((KEEP + 1)) | xargs -r rm --

echo "Сохранён ${target} ($(du -h "${target}" | cut -f1)); всего дампов: $(ls -1 "${BACKUP_DIR}"/db-*.sql.gz | wc -l)"
