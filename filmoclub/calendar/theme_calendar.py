"""
Календарь тем приложения.
Создается на основе THEMES_RANGES. Так что при изменении переменной, необходимо перезаписать календарь.
Для перезаписи используется функция create_theme_calendar в папке utils.
"""

from .theme_images import Themes

CALENDAR: {str: Themes} = {
    "01.12": "winter",
    "02.12": "winter",
    "03.12": "winter",
    "01.03": "spring",
    "02.03": "spring",
    "03.03": "spring",
    "01.06": "summer",
    "02.06": "summer",
    "03.06": "summer",
    "01.09": "fall",
    "02.09": "fall",
    "03.09": "fall",
    "29.12": "new_year",
    "30.12": "new_year",
    "31.12": "new_year",
    "01.01": "new_year",
    "02.01": "new_year",
    "03.01": "new_year",
    "04.01": "new_year",
    "05.01": "new_year",
    "06.01": "new_year",
    "07.01": "new_year",
    "08.01": "new_year",
    "09.01": "new_year",
    "10.01": "new_year",
    "11.01": "new_year",
    "31.10": "halloween",
}
