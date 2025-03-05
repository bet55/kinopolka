import pendulum
from settings.theme_images import THEMES_RANGES


def create_theme_calendar() -> dict[str, str]:
    """
    Функция для пересоздания календаря тем приложения, в случаи изменения THEMES_RANGES.
    Сейчас обновление календаря происходит вручную, чтобы использовать импорт python переменной, а не json файл.
    Обновляем THEMES_RANGES, вызываем функцию create_theme_calendar и копируем результат в CALENDAR.
    """
    calendar: {str: str} = dict()

    current_date = pendulum.now()
    current_year = current_date.year

    for date_range, theme in THEMES_RANGES.items():
        l_range, r_range = date_range.split('-')
        l_day, l_month = [int(i) for i in l_range.split('.')]
        r_day, r_month = [int(i) for i in r_range.split('.')]

        r_year = current_year if l_month <= r_month else current_year + 1

        l_date = current_date.set(day=l_day, month=l_month)
        r_date = current_date.set(day=r_day, month=r_month, year=r_year)

        days_dif = r_date.diff(l_date).in_days()
        for days_offset in range(days_dif + 1):
            day_str = l_date.add(days=days_offset)
            calendar[day_str.format('DD.MM')] = theme

    return calendar


res = create_theme_calendar()
print(res)
