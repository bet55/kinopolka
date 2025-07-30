import logging
from classes import MovieHandler
from lists.models import User
import json
import asyncio
import os
import random
from filmoclub.calendar.theme_settings import ImageFolders, Themes, IMAGES_PATH
from filmoclub.calendar.theme_calendar import CALENDAR
from django.conf import settings
import pendulum

logger = logging.getLogger(__name__)


class Tools:
    """
    Вспомогательный класс для генерации ссылок на случайные изображения и старт проекта с нуля
    """

    @classmethod
    def _get_current_theme(cls) -> Themes:
        """
        Вычисляем текущую тему оформления приложения

        :return: Название текущей темы, в зависимости от текущей даты.
        """
        try:
            current_date = pendulum.now(tz=settings.TIME_ZONE).format("DD.MM")
            theme = CALENDAR.get(current_date, Themes.default.value)
            logger.debug("Determined current theme: %s for date %s", theme, current_date)
            return theme
        except Exception as e:
            logger.error("Failed to determine current theme: %s", str(e))
            return Themes.default.value

    @classmethod
    def get_random_images(cls, theme: str = None) -> dict:
        """
        Получаем набор путей до изображений для размещения на странице приложения

        :return: Словарь с путями к изображениям для каждого блока на html странице.
        """

        # Вычисляем текущую тему или используем из аргумента функции
        theme = theme if hasattr(Themes, str(theme)) else cls._get_current_theme()

        return {
            "poster": cls._choose_random_image(theme, ImageFolders.poster.value),
            "navigation": cls._choose_random_image(theme, ImageFolders.navigation.value),
            "header": cls._choose_random_image(theme, ImageFolders.header.value),
            "postcard": cls._choose_random_image(theme, ImageFolders.postcard.value),
        }

    @classmethod
    def _choose_random_image(cls, theme: Themes, folder: ImageFolders) -> str:
        """
        Получаем путь до случайно выбранного изображения в выбранной теме и папке.

        :return: Строка с расположением изображения.
        """
        empty_file = f"/{IMAGES_PATH}/empty.png"

        full_path = f"{IMAGES_PATH}/themes/{theme}/{folder}"

        file_names = os.listdir(full_path)
        if not file_names:
            logger.warning("No images found in %s", full_path)
            return empty_file

        random_img = random.choice(file_names)

        return f"/{full_path}/{random_img}"

    async def init_project(self):
        # self.check_project_pre_creation()
        await self.create_users()
        await self.save_movies_to_db()

    def check_project_pre_creation(self):
        users = User.objects.all()
        if len(users) > 1:
            raise Exception("В системе уже есть пользователи")
        if len(users) < 1:
            raise Exception("Сперва создайте супер пользователя")

    async def create_users(self):
        url = f"/{IMAGES_PATH}/avatars/"
        users = [
            {
                "username": "drbloody1",
                "first_name": "Алексей",
                "last_name": "Губин",
                "avatar": url + "drbloody1.jpg",
            },
            {
                "username": "daenillando",
                "first_name": "Александр",
                "last_name": "Бусыгин",
                "avatar": url + "Deputant.png",
            },
            {
                "username": "Deputant",
                "first_name": "Никита",
                "last_name": "Шулаев",
                "avatar": url + "Deputant.jpg",
            },
            {
                "username": "lightthouse",
                "first_name": "Степан",
                "last_name": "Казанцев",
                "avatar": url + "lightthouse1.jpg",
            },
        ]

        results = []
        for user in users:
            user_model, status = await User.objects.aupdate_or_create(**user)
            results.append({user["username"]: status})

        return results

    async def save_movies_to_db(self) -> dict:
        movies_json = "data/movies_to_watch_dump.json"
        archive_movies_json = "data/archive_movies_dump.json"

        failed_movies_file = "data/failed_movies.json"
        error_file = "data/save_error.json"

        with open(archive_movies_json, "r") as f:
            archive_movies = json.load(f)
            archive_movies = [
                {**arch, **{"is_archive": True}} for arch in archive_movies
            ]

        with open(movies_json, "r") as f:
            movies = json.load(f)

        all_movies = movies + archive_movies

        async def export(mv_info):
            try:
                await MovieHandler.a_download(mv_info.get("id", -1), mv_info)
                return {"success": True, "id": mv_info.get("id", -1)}
            except Exception as exp:
                return {
                    "success": False,
                    "id": mv_info.get("id", -1),
                    "message": str(exp),
                }

        tasks = [export(movie) for movie in all_movies]
        tasks_result = await asyncio.gather(*tasks)

        success_results_count = len([r for r in tasks_result if r["success"] is True])
        bad_results = [r for r in tasks_result if r["success"] is False]

        with open(failed_movies_file, "w") as f:
            f.write(json.dumps(bad_results, indent=4, ensure_ascii=False))

        return {"success_count": success_results_count, "all_count": len(all_movies)}
