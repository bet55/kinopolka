#!/usr/bin/env python3
"""
Пережимает АНИМИРОВАННЫЕ webp (несколько кадров) через Pillow.

Зачем отдельный скрипт: compress_static.sh работает на ffmpeg, а ffmpeg
не умеет декодировать анимированный webp (падает "image data not found").
Поэтому "живые" постеры тем (static/img/themes/*/poster/*.webp) он пропускает.

Что делает со ВСЕМИ анимированными webp в папке-цели:
  - при необходимости уменьшает разрешение, чтобы вписать в рамку MAX_W x MAX_H
    (только уменьшение, пропорции сохраняются);
  - перекодирует все кадры с качеством QUALITY, RGB если альфа не используется;
  - сохраняет длительности кадров и зацикливание.

Идемпотентность: результат применяется, только если он ощутимо меньше
оригинала (выигрыш >= MIN_GAIN). Повторное перекодирование уже сжатого файла
даёт лишь пару процентов (дрейф libwebp) и отклоняется — значит качество не
деградирует от повторных прогонов. Статичные (одно-кадровые) webp не трогаются
— их сожмёт compress_static.sh.

Использование (из корня проекта):
    uv run scripts/compress_animated_webp.py                        # static/img/themes
    uv run scripts/compress_animated_webp.py static/img/themes      # то же явно
    uv run scripts/compress_animated_webp.py static/img/foo 512 512 # своя рамка

Результат нужно закоммитить в git.
"""

import os
from pathlib import Path
import sys
import tempfile

from PIL import Image


# ============ НАСТРОЙКИ ============
# Папка-цель: аргумент 1, по умолчанию картинки тем.
TARGET_DIR = sys.argv[1] if len(sys.argv) > 1 else "static/img/themes"

# Рамка (максимальные ширина/высота). Больше — уменьшаем; меньше — не трогаем.
MAX_W = int(sys.argv[2]) if len(sys.argv) > 2 else 432
MAX_H = int(sys.argv[3]) if len(sys.argv) > 3 else 768

# Качество webp (0-100). Выше — лучше картинка и больше размер.
QUALITY = 72
# Уровень сжатия libwebp (0-6). Выше — меньше файл, но заметно дольше.
METHOD = 4
# Минимальный выигрыш, при котором результат применяется (0.10 = 10%).
# Отсекает "дрейф" повторного перекодирования и даёт идемпотентность.
MIN_GAIN = 0.10
# ===================================

# Скрипт лежит в scripts/, а пути-цели заданы относительно корня проекта.
os.chdir(Path(__file__).resolve().parent.parent)


def load_frames(im: Image.Image) -> tuple[list[Image.Image], list[int]]:
    """Читает все кадры анимации и их длительности."""
    frames, durations = [], []
    i = 0
    try:
        while True:
            im.seek(i)
            durations.append(im.info.get("duration", 80))
            frames.append(im.convert("RGBA").copy())
            i += 1
    except EOFError:
        pass
    return frames, durations


def uses_alpha(frames: list[Image.Image]) -> bool:
    """True, если хоть один кадр реально использует прозрачность."""
    return any(f.getchannel("A").getextrema()[0] < 255 for f in frames)


def target_size(w: int, h: int) -> tuple[int, int]:
    """Размер после вписывания в рамку MAX_W x MAX_H (только уменьшение)."""
    scale = min(MAX_W / w, MAX_H / h, 1.0)
    return (round(w * scale), round(h * scale))


def compress_one(path: Path) -> tuple[str, int, int]:
    """
    Пережимает один файл на месте, если результат меньше.
    Возвращает (статус, было_байт, стало_байт).
    """
    src_size = path.stat().st_size
    with Image.open(path) as im:
        if getattr(im, "n_frames", 1) <= 1:
            return "static", src_size, src_size  # не анимация — пропускаем
        frames, durations = load_frames(im)

    w, h = frames[0].size
    new_w, new_h = target_size(w, h)
    if (new_w, new_h) != (w, h):
        frames = [f.resize((new_w, new_h)) for f in frames]

    mode = "RGBA" if uses_alpha(frames) else "RGB"
    frames = [f.convert(mode) for f in frames]

    with tempfile.NamedTemporaryFile(suffix=".webp", delete=False, dir=path.parent) as tmp:
        tmp_path = Path(tmp.name)
    try:
        frames[0].save(
            tmp_path,
            save_all=True,
            append_images=frames[1:],
            duration=durations,
            loop=0,
            quality=QUALITY,
            method=METHOD,
        )
        dst_size = tmp_path.stat().st_size
        if dst_size > src_size * (1 - MIN_GAIN):
            tmp_path.unlink()
            return "kept", src_size, src_size  # выигрыш мал — оставляем оригинал
        tmp_path.replace(path)
        return "done", src_size, dst_size
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise


def main() -> None:
    target = Path(TARGET_DIR)
    if not target.is_dir():
        print(f"Папка не найдена: {target}")
        sys.exit(1)

    webps = sorted(target.rglob("*.webp"))
    print("Пережатие анимированных webp через Pillow.")
    print(f"Папка:    {target}")
    print(f"Рамка:    {MAX_W}x{MAX_H} (только уменьшение)")
    print(f"Качество: {QUALITY}, method={METHOD}")
    print(f"Найдено webp-файлов: {len(webps)} (статичные будут пропущены)")
    print()
    if input("Начать сжатие? [y/N] ").strip().lower() not in {"y", "yes"}:
        print("Отменено.")
        return

    done = kept = static = errors = 0
    before = after = 0
    for path in webps:
        try:
            status, src, dst = compress_one(path)
        except Exception as e:  # утилита: показываем ошибку и идём дальше
            print(f"  ОШИБКА: {path} — {e}")
            errors += 1
            continue

        if status == "done":
            done += 1
            before += src
            after += dst
            print(f"  {path}  {src / 1048576:.2f}→{dst / 1048576:.2f} MB")
        elif status == "kept":
            kept += 1
        else:
            static += 1

    print()
    print("================ ИТОГО ================")
    print(f"  сжато:               {done}")
    print(f"  без изменений:       {kept}")
    print(f"  статичных (пропуск): {static}")
    print(f"  ошибок:              {errors}")
    print(f"  было:  {before / 1048576:.1f} MB")
    print(f"  стало: {after / 1048576:.1f} MB")
    print(f"  сэкономлено: {(before - after) / 1048576:.1f} MB")
    print("=======================================")
    print("Не забудь закоммитить изменения в git.")


if __name__ == "__main__":
    main()
