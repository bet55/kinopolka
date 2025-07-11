# Чайный киноклуб

![img](https://mir-s3-cdn-cf.behance.net/project_modules/max_1200/3719ec13417329.5627bb2646088.jpg)

Приложение призванное увековечить киноклубные вечера, а также
разнообразить их наполнение активностями.

http://185.80.91.29:8000/

Реализованно:
1. Архив просмотренного
2. Список для просмотра
3. Именные пользователи
4. Рулетка для выбора фильма
5. Открытка с будущими фильмами
6. Архив открыток с сеансами
7. Теги для фильтрации фильмов
8. Сортировка фильмов

Может быть:
1. Игровой выбор фильмов (турнир, квиз по фильмам)
2. Добавить рубрику "Угадай кино"
3. Список выпитого чая/коктейлей
4. Голосование за фильмы
5. Текущее состояние бара
6. Фильтры для статистики

Логи приложения:  
http://185.80.91.29:3000/



# Скопируем все необходимые файлы для старта
__копировать базу данных из сервера__  
scp root@185.80.91.29:/var/www/kinopolka/db.sqlite3 /home/stephan/projects/vps_db

__копировать открытки из сервера__  
scp root@185.80.91.29:/var/www/kinopolka/media/postcards/* /home/stephan/projects/kinopolka/media/postcards/

__копировать постеры из сервера__  
scp root@185.80.91.29:/var/www/kinopolka/media/posters/* /home/stephan/projects/kinopolka/media/posters/

__копировать start.sh файл из сервера__  
scp root@185.80.91.29:/var/www/kinopolka/start.sh /home/stephan/projects/kinopolka/start.sh

# Старт приложения
- В файле **start.sh** выбрать нужные переменные окружения (local или dev)
- Запустить докер контейнер grafana/loki (иначе логи не смогут записываться)
- Запустить докер контейнер django либо файл _start.sh_

# Разрешение ошибок
1. Сохранение открытки создает картинку с пустыми рамками, вместо постеров.
   - Это проблема на стороне библиотеке. В автоматическом режиме пока что не получается её обнаружить.
   - Просто, удалите получившуюся открытку и попытайтесь снова.  
2. Отсутствие постеров фильмов.
   - Нестабильное api по возвращению картинок. Из-за этого в базе может не сохраниться изображение. 
   - Для решения. Запустите скрипт ` uv run manage.py download_posters`
   - Если в процессе сохранения образовались дублирующие постеры, удалите их скриптом `cleanup_posters.sh`
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