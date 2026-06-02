# Чайный киноклуб

![img](https://mir-s3-cdn-cf.behance.net/project_modules/max_1200/3719ec13417329.5627bb2646088.jpg)

Приложение призванное увековечить киноклубные вечера, а также
разнообразить их наполнение активностями.

https://kinopolka.com/
https://kinopolka.рф/

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

Может быть:
1. Игровой выбор фильмов (турнир, квиз по фильмам)
2. Добавить рубрику "Угадай кино"
3. Раздел с фото клуба

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
базу данных db.sqlite3 и файл для старта приложения start.sh с сервера:
    ```bash
    bash sync_from_remote.sh
    ```
4. В start.sh меняем переменную с prod на dev
5. uv sync - установить зависимости
6. uv run pre-commit install - установить гит хук

# Разрешение ошибок
- Если ссылки на дублирующие постеры попали в бд, замените их командой `uv run manage.py fix_posters_names`

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
