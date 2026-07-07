import logging
import os
import random

from django.conf import settings
import pendulum

from filmoclub.calendar.theme_calendar import CALENDAR
from filmoclub.calendar.theme_settings import IMAGES_PATH, ImageFolders, Themes


logger = logging.getLogger(__name__)


class Tools:
    """
    Вспомогательный класс для генерации ссылок на случайные изображения
    """

    @classmethod
    def get_current_theme(cls) -> Themes:
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
    def get_random_images(cls, theme: str | Themes = None) -> dict:
        """
        Получаем набор путей до изображений для размещения на странице приложения

        :return: Словарь с путями к изображениям для каждого блока на html странице.
        """

        # Вычисляем текущую тему или используем из аргумента функции
        theme = theme if hasattr(Themes, str(theme)) else cls.get_current_theme()

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
