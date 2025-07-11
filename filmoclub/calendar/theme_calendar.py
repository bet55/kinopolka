"""
Календарь тем приложения.
Создается на основе THEMES_RANGES. Так что при изменении переменной, необходимо перезаписать календарь.
Для перезаписи используется функция create_theme_calendar в папке utils.
"""

from .theme_settings import Themes

CALENDAR: {str: Themes} = {'18.12': 'Danya', '01.06': 'Lexa', '21.03': 'Nikita', '19.06': 'Sanya', '01.09': 'fall',
                           '02.09': 'fall', '03.09': 'fall', '04.09': 'fall', '05.09': 'fall', '06.09': 'fall',
                           '07.09': 'fall', '08.09': 'fall', '31.10': 'halloween', '01.01': 'new_year',
                           '02.01': 'new_year', '03.01': 'new_year', '04.01': 'new_year', '05.01': 'new_year',
                           '06.01': 'new_year', '07.01': 'new_year', '08.01': 'new_year', '09.01': 'new_year',
                           '10.01': 'new_year', '11.01': 'new_year', '29.12': 'new_year', '30.12': 'new_year',
                           '31.12': 'new_year', '01.03': 'spring', '02.03': 'spring', '03.03': 'spring',
                           '04.03': 'spring', '05.03': 'spring', '06.03': 'spring', '07.03': 'spring',
                           '08.03': 'spring', '02.06': 'summer', '03.06': 'summer', '04.06': 'summer',
                           '05.06': 'summer', '06.06': 'summer', '07.06': 'summer', '08.06': 'summer',
                           '01.12': 'winter', '02.12': 'winter', '03.12': 'winter', '04.12': 'winter',
                           '05.12': 'winter', '06.12': 'winter', '07.12': 'winter', '08.12': 'winter'}
