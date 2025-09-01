"""
Календарь тем приложения.
Создается на основе THEMES_RANGES. Так что при изменении переменной, необходимо перезаписать календарь.
Для перезаписи используется функция create_theme_calendar в папке utils.
"""

from .theme_settings import Themes

CALENDAR: {str: Themes} = {'01.12': 'winter', '02.12': 'winter', '03.12': 'winter', '04.12': 'winter',
                           '05.12': 'winter', '06.12': 'winter', '07.12': 'winter', '08.12': 'winter',
                           '09.12': 'winter', '10.12': 'winter', '11.12': 'winter', '12.12': 'winter',
                           '13.12': 'winter', '14.12': 'winter', '15.12': 'winter',

                           '01.03': 'spring', '02.03': 'spring', '03.03': 'spring', '04.03': 'spring',
                           '05.03': 'spring', '06.03': 'spring', '07.03': 'spring', '08.03': 'spring',
                           '09.03': 'spring', '10.03': 'spring', '11.03': 'spring', '12.03': 'spring',
                           '13.03': 'spring', '14.03': 'spring', '15.03': 'spring',

                           '02.06': 'summer', '03.06': 'summer',
                           '04.06': 'summer', '05.06': 'summer', '06.06': 'summer', '07.06': 'summer',
                           '08.06': 'summer', '09.06': 'summer', '10.06': 'summer', '11.06': 'summer',
                           '12.06': 'summer', '13.06': 'summer', '14.06': 'summer', '15.06': 'summer',

                           '01.09': 'fall',
                           '02.09': 'fall', '03.09': 'fall', '04.09': 'fall', '05.09': 'fall', '06.09': 'fall',
                           '07.09': 'fall', '08.09': 'fall', '09.09': 'fall', '10.09': 'fall', '11.09': 'fall',
                           '12.09': 'fall', '13.09': 'fall', '14.09': 'fall', '15.09': 'fall',

                           '21.03': 'Nikita',
                           '01.06': 'Lexa', '19.06': 'Sanya', '18.12': 'Danya',

                           '29.12': 'new_year',
                           '30.12': 'new_year', '31.12': 'new_year', '01.01': 'new_year', '02.01': 'new_year',
                           '03.01': 'new_year', '04.01': 'new_year', '05.01': 'new_year', '06.01': 'new_year',
                           '07.01': 'new_year', '08.01': 'new_year', '09.01': 'new_year', '10.01': 'new_year',
                           '11.01': 'new_year',

                           '31.10': 'halloween'}
