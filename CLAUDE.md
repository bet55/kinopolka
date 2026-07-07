# CLAUDE.md

Заметки для работы над проектом «Чайный киноклуб» (kinopolka).

## Что это
Django 5.1 + DRF + `adrf` (async views) — приложение для просмотра кино с друзьями.
Прод: https://kinopolka.com, https://kinopolka.рф. База — SQLite (`db.sqlite3`).

## Приложения
- `lists` — фильмы, оценки/заметки (`Note`), пользователи. Основной домен.
- `postcard` — открытки-приглашения на сеанс (с рассылкой в Telegram/email).
- `features` — статистика, казино, каталог, таро, «качалка».
- `bar` — коктейли и ингредиенты.
- `tools` — темы оформления и прочее.

## Архитектура
- **Views тонкие** (`*/views.py`, async `adrf.APIView`), вся логика — в `classes/*`
  (handler-паттерн: `MovieHandler`, `NoteHandler`, `PostcardHandler`, `UserHandler`,
  `KP_Movie`, `Caching`, `Tools`, `Statistic`).
- **Валидация ответов Кинопоиска** — pydantic v2 модели в `pydantic_models/`.
- `mixins/global_data.py` (`GlobalDataMixin`) добавляет users/theme/random в контекст шаблонов.
- Данные о фильмах — из неофициального API Кинопоиска (`classes/kp.py`), кэш через `diskcache`.
- Темы (сезонные/именинные) читаются через `os.listdir` в `classes/tools.py`.

## Доступ: tea_code вместо авторизации
Полноценной авторизации нет **осознанно** (узкий круг друзей, не хотим громоздкости).
`TeaCodeMiddleware` (`utils/middleware.py`): изменяющие запросы (POST/PUT/PATCH/DELETE)
требуют верный `tea_code` (env `TEA_CODE` из `env.sh`), просмотр открыт всем —
чтобы можно было показывать сайт посторонним без риска «случайно нажать».
Вход — ссылкой `?tea_code=XXX`, дальше код живёт в HttpOnly-куке на год; JS про него
не знает. `/boss/` (админка) исключён — там своя авторизация. Пустой `TEA_CODE`
отключает проверку. Смена кода в `env.sh` отзывает все старые ссылки и куки.

## Админка
Django admin на **`/boss/`** (не /admin/ — тот отдаёт 404). Зарегистрированы модели
всех приложений (lists, postcard, bar, features). Суперпользователь создаётся
автоматически при старте: `DJANGO_SUPERUSER_USERNAME`/`DJANGO_SUPERUSER_PASSWORD`
в `env.sh` + вызов `createsuperuser --noinput` в `start.sh` (повторный запуск безвреден).

## Обработка ошибок (важно)
Своя схема, НЕ нативный DRF-handler (решено оставить как есть):
- `@handle_exceptions("Ресурс")` (`utils/exception_handler.py`) ловит исключения и
  **возвращает** `{'error': {'message', 'status'}}` (не поднимает).
- View прогоняет результат через `handle_response(...)` (`utils/response_handler.py`),
  который превращает error-dict в DRF `Response` с нужным статусом.
- Человекочитаемый текст → `raise ValidationError("текст")` (DRF-овый) внутри хендлера.
- Заготовка нативного варианта лежит в `utils/drf_exception_handler.py` (в `settings.py`
  закомментирована) — на будущее, если решим мигрировать.

### Грабли pydantic v2
`ValidationError` — это `from pydantic import ValidationError`, а **НЕ** `Model.ValidationError`
(у модели такого атрибута нет → обращение бросает `AttributeError` прямо в момент
сопоставления `except`, маскируя настоящую ошибку). В классах уже импортируется DRF-овый
`ValidationError`, поэтому pydantic-овый берём под алиасом:
`from pydantic import ValidationError as PydanticValidationError`.

## Запуск и разработка
- Зависимости: `uv sync`. Запуск команд: `uv run ...`.
- Старт приложения: `bash start.sh` (он в git — чистая логика). Все секреты и
  окружение — в `env.sh` (вне git; шаблон `example_env.sh`), start.sh сам его
  подключает. Переменная `ENVIRONMENT=dev|prod` переключает DEBUG/хосты/SSL/порт.
- Management-командам с секретами (`update_recent_movies`, `download_posters`)
  нужно `source env.sh` перед запуском — иначе «Missing API key».
- Линт/хуки: `ruff` + `pre-commit` (`uv run pre-commit install`).
- Тестов практически нет (`*/tests.py` — заглушки).

## Скрипты (`scripts/`, запускать из корня)
- `sync_from_remote.sh` — тянет с VPS `db.sqlite3`, `env.sh`, `media/*`.
- `backup_vps_settings.sh` — бэкап конфигов VPS (nginx/ufw/fail2ban).
- `compress_static.sh` — ffmpeg: статичные `png/jpg/gif → webp`.
- `compress_animated_webp.py` — Pillow: **анимированные** webp (ffmpeg их не декодирует!).
- `reset.sh` — `flush` БД + миграции (осторожно).
- `start.sh` (в git) / `env.sh` (вне git) / `example_env.sh` остаются в корне;
  env.sh тянется sync-ом с VPS.

Management-команды: `download_posters`, `fix_posters_names`, `delete_unused_postcards`,
`update_recent_movies` (обновление оценок/сборов у свежих фильмов),
`update_theme_calendar` (печатает календарь тем из `THEMES_RANGES`; результат
вручную копируется в `filmoclub/calendar/theme_calendar.py`).
Подробнее — раздел «Скрипты и обслуживание» в `README.md`.
