from enum import Enum


IMAGES_PATH = "static/img"


class ImageFolders(Enum):
    """
    Названия папок, в которых лежат соответствующие изображения оформления приложения.
    """

    header = "header"
    navigation = "navigation"
    poster = "poster"
    postcard = "postcard"


class Themes(Enum):
    """
    Список тем оформления приложения. В основном, набор картинок.
    Названия должны совпадать с названиями тем в папке static/img/themes
    """

    default = "default"
    new_year = "new_year"
    halloween = "halloween"
    summer = "summer"
    spring = "spring"
    fall = "fall"
    winter = "winter"

    Lexa = "Lexa"
    Sanya = "Sanya"
    Nikita = "Nikita"
    Danya = "Danya"


# Каким временным отрезкам соответствуют темы
# Из отрезков формируется календарь
THEMES_RANGES = {
    "01.12-08.12": Themes.winter.value,
    "01.03-08.03": Themes.spring.value,
    "02.06-08.06": Themes.summer.value,
    "01.09-08.09": Themes.fall.value,

    "01.06-01.06": Themes.Lexa.value,
    "19.06-19.06": Themes.Sanya.value,
    "18.12-18.12": Themes.Danya.value,

    "29.12-11.01": Themes.new_year.value,
    "31.10-31.10": Themes.halloween.value,
}
