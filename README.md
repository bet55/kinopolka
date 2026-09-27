# Чайный киноклуб

![img](https://mir-s3-cdn-cf.behance.net/project_modules/max_1200/3719ec13417329.5627bb2646088.jpg)

Приложение призванное увековечить киноклубные вечера, а также
разнообразить их наполнение активностями.

https://kinopolka.com/

Реализованно:
1. Архив просмотренного
2. Список для просмотра
3. Именные пользователи
4. Рулетка для выбора фильма
5. Открытка с грядущими фильмами на просмотр
6. Архив открыток с сеансами
7. Теги для фильтрации фильмов
8. Сортировка фильмов
9. Текущее состояние бара
10. Таро!
11. Раздел с фото киноклуба
12. Наполненность бара
13. Статистика по просмотру
14. Игровой выбор фильмов

Логи приложения:
https://kinopolka.com/application/grafana/

# Настройка на новом устройстве
1. Скачиваем код проекта из GitHub
2. На VPS убираем дубликаты постеров (запускать из корня проекта):
   ```bash
   cd /var/www/kinopolka
   cp db.sqlite3 db.sqlite3.bak          # бэкап БД на всякий случай
   uv run manage.py fix_posters_names
   ```
3. Локально выкачиваем медиа файлы для постеров, открыток, коктейлей и ингредиентов;
базу данных db.sqlite3 и файл с переменными окружения env.sh с сервера. Не забудь указать
в скрипте путь до локального проекта
    ```bash
    bash scripts/sync_from_remote.sh
    ```
   (если сервера под рукой нет — `cp example_env.sh env.sh` и заполнить руками)
4. В env.sh меняем переменную с prod на dev, ставим свой `APP_PORT`.
Добавляем tea_code для авторизации пользователей.
5. uv sync - установить зависимости
6. uv run pre-commit install - установить гит хук
7. Суперпользователь для админки (`/boss/`) создаётся автоматически при старте:
заполни `DJANGO_SUPERUSER_USERNAME` / `DJANGO_SUPERUSER_PASSWORD` в env.sh
(пустой логин — шаг пропускается). База локальная, поэтому пользователь заведётся
на каждой машине при первом запуске.

## Переменные окружения и разовые команды
Разделение ролей:
- **`env.sh`** (вне git, у каждой машины свой; шаблон `example_env.sh`) — все
  переменные: секреты, порт, настройки. Устроен так: сначала базовые значения
  (= dev-режим), затем блок `if [ "$ENVIRONMENT" = "prod" ]`, который
  переопределяет часть переменных для прода (DEBUG, хосты, порт 8000, SSL).
  То есть один и тот же файл по структуре работает и локально, и на VPS —
  различие только в строке `ENVIRONMENT=dev|prod`.
- **`start.sh`** логика запуска:
  подключает env.sh, собирает статику, создаёт суперпользователя, стартует сервер.

Management-командам, которым нужны секреты (`update_recent_movies`,
`download_posters`), окружение втягивается вручную:
```bash
source env.sh    # один раз на сессию терминала (в докере: . ./env.sh)
uv run manage.py update_recent_movies
```

# Разрешение ошибок
- Если ссылки на дублирующие постеры попали в бд, замените их командой `uv run manage.py fix_posters_names`

# Скрипты и обслуживание

Операционные скрипты лежат в папке `scripts/` (запускать из корня проекта).
В корне остаются: `start.sh` (точка входа, в git), `env.sh` (переменные
окружения, вне git — тянется с VPS через sync) и шаблон `example_env.sh`.

## Схема работы (что откуда берётся)

```
                 Kinopoisk API                        VPS (prod)
                      │                                    │
   manage.py         │ download_posters                   │ sync_from_remote.sh
   ─────────         ▼                                     ▼
   media/posters/ ◄── постеры фильмов          db.sqlite3 + env.sh + media/* ──► локально
        │                                                  │ backup_vps_settings.sh
        │ fix_posters_names (чистка имён/дублей)           ▼
        ▼                                          nginx/ufw/fail2ban конфиги ──► бэкап вне репо
   media/postcards/ ◄── delete_unused_postcards (удаление сирот)

   db.sqlite3 ──► audit_movies (только чтение) ──► movies_audit.txt
        ▲                                              │ что дозалить
        └── fill_missing_data ◄── Kinopoisk API ◄───────┘

   static/img/  ──► compress_static.sh (ffmpeg: png/jpg/gif → webp)
                └─► compress_animated_webp.py (Pillow: анимированные webp)
```

## Скрипты в `scripts/`

| Скрипт | Что делает | Пример запуска |
|---|---|---|
| `sync_from_remote.sh` | Скачивает с VPS `db.sqlite3`, `env.sh` и всё `media/*` (rsync `--ignore-existing` — уже скачанное не трогает). | `bash scripts/sync_from_remote.sh` |
| `backup_vps_settings.sh` | Бэкап конфигов VPS (nginx/ufw/fail2ban) в папку вне репозитория. | `bash scripts/backup_vps_settings.sh` |
| `compress_static.sh` | Сжимает статичные картинки в WebP через ffmpeg (png/jpg → webp, gif → анимированный webp). Исходники заменяются на `.webp`. | `bash scripts/compress_static.sh static/img/themes` |
| `compress_animated_webp.py` | Пережимает **анимированные** webp через Pillow (ffmpeg их не декодирует). Вписывает в рамку 432×768, идемпотентно. | `uv run scripts/compress_animated_webp.py static/img/themes` |
| `reset.sh` | `flush` БД + миграции. Осторожно: стирает данные. | `bash scripts/reset.sh` |

## Management-команды (по данным БД)

Работают напрямую с базой (кроме `update_theme_calendar`) — запущенное приложение
НЕ требуется. Но командам, которые ходят в API Кинопоиска (`update_recent_movies`,
`download_posters`, `fill_missing_data`), нужны переменные окружения — сначала
`source env.sh` (один раз на сессию терминала).

Пример: обновить информацию о свежих фильмах —
```bash
source env.sh
uv run manage.py update_recent_movies
```

| Команда | Что делает |
|---|---|
| `uv run manage.py download_posters` | Скачивает/привязывает постеры фильмов из Кинопоиска в `media/posters/`. Нужен `source env.sh`. |
| `uv run manage.py fix_posters_names` | Убирает случайные суффиксы из имён постеров и дедуплицирует файлы. |
| `uv run manage.py delete_unused_postcards` | Удаляет файлы открыток, которых нет в БД. |
| `uv run manage.py update_recent_movies` | Обновляет оценки KP/IMDb, голоса и кассовые сборы у фильмов с премьерой за последние N лет (`--years`, `--dry-run`, `--limit`, `--delay`). Нужен `source env.sh`. |
| `uv run manage.py update_theme_calendar` | Пересобирает календарь тем оформления из `THEMES_RANGES` и печатает его. БД не трогает; результат вручную копируется в `CALENDAR` (`filmoclub/calendar/theme_calendar.py`) — календарь осознанно хранится python-переменной, а не json-файлом. Запускать после изменения `THEMES_RANGES` в `filmoclub/calendar/theme_settings.py`. |
| `uv run manage.py audit_movies` | Ищет фильмы с недостающими данными и пишет отчёт в файл (`--output`, `--daily-limit`). Только читает БД, в API не ходит — лимит запросов не тратит. |
| `uv run manage.py fill_missing_data` | Дозаливает найденные пробелы: жанры, персон, пустые поля карточки (`--only`, `--limit`, `--delay`, `--retries`, `--dry-run`). Один фильм — один запрос к API, нужен `source env.sh`. |

## Дозаливка недостающих данных

Пара команд `audit_movies` → `fill_missing_data`. Что считать пробелом — одно
определение на обе, `MovieHandler.find_missing` (`classes/movie.py`), так что
отчёт и дозаливка не могут разойтись.

Главное, ради чего всё затевалось: фильм без жанров на странице виден, но
выпадает из любого фильтра по жанрам — глазами такое не заметишь.

Порядок работы — снять отчёт, залить, снять второй и сравнить:

```bash
uv run manage.py audit_movies --output movies_audit_before.txt

source env.sh
uv run manage.py fill_missing_data --dry-run     # посмотреть, что будет запрошено
uv run manage.py fill_missing_data               # собственно дозаливка

uv run manage.py audit_movies --output movies_audit_after.txt
diff movies_audit_before.txt movies_audit_after.txt
```

Отчёты (`movies_audit*.txt`) в `.gitignore` — файлы локальные. Имя задаётся
через `--output`; без него оба прогона запишутся в один `movies_audit.txt`
и сравнивать будет не с чем.

Про лимит API: `audit_movies` в шапке отчёта сам считает, сколько фильмов
требуют запроса и на сколько дней это растянется при `--daily-limit`. Если не
влезает в сутки — режь запуск через `--limit`, остальное доберётся следующим.
`--only genres` — самый дешёвый прогон, когда важен только фильтр по жанрам.

Чего команда НЕ трогает: непустые поля, оценки клуба, `watch_date` и
`is_archive`. Заполняются только пробелы, каждый фильм — своей транзакцией,
поэтому сбой на одном не рушит остальные. Постеры сюда не входят — это
`download_posters`, и в отчёте такая строка помечена без `[API]`.

## Сжатие изображений

Два инструмента дополняют друг друга и не пересекаются:

- **`compress_static.sh`** (ffmpeg) — для статичных `png/jpg/jpeg/gif`. ffmpeg
  не умеет декодировать анимированный webp, поэтому такие файлы он пропускает.
- **`compress_animated_webp.py`** (Pillow) — для анимированных webp («живые»
  постеры тем). Уменьшает разрешение под рамку, перекодирует все кадры и
  применяет результат только при существенном выигрыше (идемпотентность).

Папки тем читаются через `os.listdir` (`classes/tools.py`), поэтому смена
формата на `.webp` кода не требует. Для картинок, на которые ссылаются по
точному имени (иконки UI, `mb/`-гифки на странице 404), ссылки нужно править
вручную — их не конвертируем.

[kinorium](https://ru.kinorium.com/collections/kinorium/)
[постеры](https://www.movieposters.com/)

[figma](https://www.figma.com/design/iEelBzbgfnGmk810JXHGGn/%D0%BA%D0%B8%D0%BD%D0%BE%D0%BA%D0%BB%D1%83%D0%B1?node-id=0-1&node-type=canvas&t=ZwrMRzvz8z7EbmCr-0)
[github](https://github.com/bet55/kinopolka)
[kanban](https://github.com/users/bet55/projects/2)
[github old](https://github.com/bet55/-)
[kinopoisk](https://www.kinopoisk.ru/mykp/folders/4583/?format=posters&limit=50)
[kinopoisk api](https://api.kinopoisk.dev/documentation#/)

Использованы изображения со следующих сайтов:
https://www.flaticon.com
https://www.pngwing.com
