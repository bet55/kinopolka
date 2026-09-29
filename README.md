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
15. Админ панель

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
8. Запускаем командой sh start.sh или через docker compose up -d

## Переменные окружения и разовые команды
Разделение ролей:
- **`env.sh`** переменные окружения
- **`start.sh`** логика запуска:
  подключает env.sh, собирает статику, создаёт суперпользователя, стартует сервер.


## Скрипты в `scripts/`

| Скрипт | Что делает | Пример запуска |
|---|---|---|
| `sync_from_remote.sh` | Скачивает с VPS `db.sqlite3`, `env.sh` и всё `media/*` (rsync `--ignore-existing` — уже скачанное не трогает). | `bash scripts/sync_from_remote.sh` |
| `backup_vps_settings.sh` | Бэкап конфигов VPS (nginx/ufw/fail2ban) в папку вне репозитория. | `bash scripts/backup_vps_settings.sh` |
| `compress_static.sh` | Сжимает статичные картинки в WebP через ffmpeg (png/jpg → webp, gif → анимированный webp). Исходники заменяются на `.webp`. | `bash scripts/compress_static.sh static/img/themes` |
| `compress_animated_webp.py` | Пережимает **анимированные** webp через Pillow (ffmpeg их не декодирует). Вписывает в рамку 432×768, идемпотентно. | `uv run scripts/compress_animated_webp.py static/img/themes` |
| `reset.sh` | `flush` БД + миграции. Осторожно: стирает данные. | `bash scripts/reset.sh` |

## Management-команды

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



Логи приложения:
Сейчас не ведутся. Так как докер конейнер с графаной на сервере неактивен.
Для возобновления работы, нужно поднять соответстующий контейнер на vps.
Чтобы работало локлаьно, нужно поменять настройки логера в settings.py.
[Ссылка на логи](https://kinopolka.com/application/grafana/)




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

![](/static/img/mb/mb4.jpg)
