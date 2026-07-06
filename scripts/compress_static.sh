#!/usr/bin/env bash
#
# Сжимает картинки в WebP с помощью ffmpeg:
#   - GIF  -> анимированный WebP
#   - PNG/JPG -> WebP (lossy)
#
# Использование (из корня проекта):
#   ./scripts/compress_static.sh                         # темы (по умолчанию), все форматы
#   ./scripts/compress_static.sh static/img/tarots png   # только png в указанной папке
#   ./scripts/compress_static.sh static/img/carousel png #
#
# Если папка-цель читается через os.listdir() (как темы в classes/tools.py),
# смена расширения на .webp правок кода НЕ требует. Для папок со ссылками по
# имени (tarots, carousel) ссылки нужно поправить отдельно.
#
# Идемпотентность: исходник удаляется после конвертации, при повторном запуске
# в папке остаются только .webp — их скрипт не трогает. Новые картинки сожмутся
# на следующем прогоне. Результат нужно закоммитить в git.
#
set -euo pipefail

# ============ НАСТРОЙКИ ============
# Папка-цель: аргумент 1, по умолчанию картинки тем.
TARGET_DIR="${1:-static/img/themes}"
shift || true

# Форматы для конвертации: остальные аргументы, по умолчанию все растровые.
EXTENSIONS=("$@")
[ "${#EXTENSIONS[@]}" -eq 0 ] && EXTENSIONS=(gif png jpg jpeg)

# Качество WebP (0-100). Выше — лучше картинка и больше размер.
PNG_JPG_QUALITY=80   # для статичных PNG/JPG
GIF_QUALITY=75       # для анимированных GIF
# ===================================

# Скрипт лежит в scripts/, а пути-цели заданы относительно корня проекта.
cd "$(dirname "$0")/.."

if [ ! -d "${TARGET_DIR}" ]; then
    echo "Папка не найдена: ${TARGET_DIR}"
    exit 1
fi

echo "Сжатие картинок в WebP."
echo "Папка:    ${TARGET_DIR}"
echo "Форматы:  ${EXTENSIONS[*]}"
echo "Качество: PNG/JPG=${PNG_JPG_QUALITY}, GIF=${GIF_QUALITY}"
echo "Исходники (${EXTENSIONS[*]}) будут заменены на .webp (удаляются)."
echo
read -r -p "Начать сжатие? [y/N] " answer
case "${answer}" in
    [yY] | [yY][eE][sS]) ;;
    *)
        echo "Отменено."
        exit 0
        ;;
esac

converted=0
skipped=0
errors=0
bytes_before=0
bytes_after=0

# Собираем выражение find из списка расширений: -iname '*.ext' -o ...
find_expr=()
for e in "${EXTENSIONS[@]}"; do
    find_expr+=(-iname "*.${e}" -o)
done
unset 'find_expr[${#find_expr[@]}-1]'  # убираем хвостовой -o

# Обрабатываем только растровые исходники; .webp не трогаем (идемпотентность).
while IFS= read -r -d '' src; do
    ext="${src##*.}"
    ext="${ext,,}"
    dst="${src%.*}.webp"

    # Выбираем кодек: анимированный для GIF, обычный для остального.
    if [ "${ext}" = "gif" ]; then
        codec="libwebp_anim"
        quality="${GIF_QUALITY}"
    else
        codec="libwebp"
        quality="${PNG_JPG_QUALITY}"
    fi

    # -nostdin обязателен: иначе ffmpeg читает из stdin и «съедает» поток,
    # которым кормится цикл while read, портя следующие пути.
    if ! ffmpeg -nostdin -y -hide_banner -loglevel error \
        -i "${src}" -c:v "${codec}" -lossless 0 -q:v "${quality}" -loop 0 "${dst}" 2>/dev/null; then
        echo "  ОШИБКА конвертации: ${src}"
        rm -f "${dst}"
        errors=$((errors + 1))
        continue
    fi

    src_size=$(stat -c%s "${src}")
    dst_size=$(stat -c%s "${dst}")

    # Защита: если WebP не меньше исходника — откатываемся, оставляем оригинал.
    if [ "${dst_size}" -ge "${src_size}" ]; then
        rm -f "${dst}"
        echo "  пропуск (WebP не меньше): ${src}"
        skipped=$((skipped + 1))
        continue
    fi

    rm -f "${src}"
    bytes_before=$((bytes_before + src_size))
    bytes_after=$((bytes_after + dst_size))
    converted=$((converted + 1))
    printf "  %s  %.2f→%.2f MB\n" "${src}" \
        "$(echo "${src_size}/1048576" | bc -l)" "$(echo "${dst_size}/1048576" | bc -l)"
done < <(find "${TARGET_DIR}" -type f \( "${find_expr[@]}" \) -print0)

echo
echo "================ ИТОГО ================"
printf "  конвертировано: %d\n" "${converted}"
printf "  пропущено:      %d\n" "${skipped}"
printf "  ошибок:         %d\n" "${errors}"
printf "  было:  %.1f MB\n" "$(echo "${bytes_before}/1048576" | bc -l)"
printf "  стало: %.1f MB\n" "$(echo "${bytes_after}/1048576" | bc -l)"
printf "  сэкономлено: %.1f MB\n" "$(echo "(${bytes_before}-${bytes_after})/1048576" | bc -l)"
echo "======================================"
echo "Не забудь закоммитить изменения в git."
