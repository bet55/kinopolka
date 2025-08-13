from django.core.management.base import BaseCommand

from filmoclub.calendar.theme_calendar import CALENDAR
from utils import create_theme_calendar


class Command(BaseCommand):
    help = "Обновление календаря с темами. filmoclub/theme_calendar"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Поехали"))

        new_calendar = create_theme_calendar()
        print(new_calendar)
        CALENDAR.update(new_calendar)

        self.stdout.write(self.style.SUCCESS("Приехали"))
