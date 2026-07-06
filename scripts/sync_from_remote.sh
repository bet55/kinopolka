#!/usr/bin/env bash
#
# Скачивает с удалённого сервера всё, что не хранится в git:
# базу db.sqlite3, env.sh и все медиа-файлы (media/ со всеми подпапками).
#
# Уже скачанные файлы повторно НЕ загружаются (rsync --ignore-existing).
#
set -euo pipefail

# ============ НАСТРОЙКИ ============
# Куда складывать скачанные файлы. Меняй при необходимости.
DEST_DIR="/home/stephan/projects/kinopolka"

# Параметры удалённого сервера.
REMOTE_USER="root"
REMOTE_HOST="109.120.159.182"
REMOTE_PORT="3988"
REMOTE_DIR="/var/www/kinopolka"
# ===================================

REMOTE="${REMOTE_USER}@${REMOTE_HOST}"
SSH_CMD="ssh -p ${REMOTE_PORT}"

# Одиночные файлы в корне проекта (пути относительно REMOTE_DIR).
FILES=("db.sqlite3" "env.sh")

# Сюда копим строки итоговой сводки "что : сколько".
SUMMARY=()

# Запускает rsync, показывает его вывод и возвращает число реально
# скачанных файлов в глобальную переменную LAST_COUNT.
run_rsync() {
    local out
    out=$(rsync "${RSYNC_OPTS[@]}" "$@")
    echo "${out}"
    LAST_COUNT=$(echo "${out}" | sed -n 's/^Number of regular files transferred: //p' | tr -d ', ')
    LAST_COUNT=${LAST_COUNT:-0}
}

echo "Файлы будут скачаны в:"
echo "    ${DEST_DIR}"
echo "С сервера: ${REMOTE}:${REMOTE_DIR}  (порт ${REMOTE_PORT})"
echo "Уже существующие локально файлы будут пропущены."
echo
read -r -p "Начать загрузку? [y/N] " answer
case "${answer}" in
    [yY] | [yY][eE][sS]) ;;
    *)
        echo "Отменено."
        exit 0
        ;;
esac

# -a  сохранить структуру/права, -v подробно, -h по-человечески, --progress прогресс,
# --stats  итоговая статистика (нужна для подсчёта), --ignore-existing  не трогать
# файлы, которые уже есть локально.
RSYNC_OPTS=(-avh --progress --stats --ignore-existing -e "${SSH_CMD}")

echo
echo ">>> Одиночные файлы..."
for f in "${FILES[@]}"; do
    run_rsync "${REMOTE}:${REMOTE_DIR}/${f}" "${DEST_DIR}/"
    SUMMARY+=("${f}: ${LAST_COUNT}")
done

echo
echo ">>> Медиа-файлы..."
# Определяем подпапки media прямо на сервере, чтобы новые подхватывались сами.
media_subdirs=$(${SSH_CMD} "${REMOTE}" "find '${REMOTE_DIR}/media' -mindepth 1 -maxdepth 1 -type d -printf '%f\n'")

while IFS= read -r d; do
    [ -z "${d}" ] && continue
    echo
    echo "--- media/${d} ---"
    mkdir -p "${DEST_DIR}/media/${d}"
    run_rsync "${REMOTE}:${REMOTE_DIR}/media/${d}/" "${DEST_DIR}/media/${d}/"
    SUMMARY+=("media/${d}: ${LAST_COUNT}")
done <<< "${media_subdirs}"

echo
echo "================ ИТОГО СКАЧАНО ================"
for line in "${SUMMARY[@]}"; do
    echo "  ${line}"
done
echo "=============================================="
echo "Готово."
