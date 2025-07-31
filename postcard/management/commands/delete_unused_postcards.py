import os
from pathlib import Path

from django.core.management.base import BaseCommand
from icecream import ic

from postcard.models import Postcard


class Command(BaseCommand):
    help = "Delete postcards files in media/posters/ if they don`t exist in database"

    def handle(self, *args, **options):
        ic("Удаляем изображения открыток, которых нет в базе ....")

        postcard_folder = Path("media/postcards")

        db_rows = Postcard.objects.all()
        db_postcards = set(p.screenshot.url.split("/")[-1] for p in db_rows)

        directory_postcards = {
            f.name
            for f in postcard_folder.glob("*")
            if f.is_file() and f.name != "screenshot.png"
        }

        postcards_to_delete = directory_postcards - db_postcards
        ic("Открыток в базе", len(db_postcards))
        ic("Открыток в папке", len(directory_postcards))
        ic("Открыток на удаление", len(postcards_to_delete))

        if not postcards_to_delete:
            ic("Лишних файлов нет")
            exit(0)

        for filename in postcards_to_delete:
            file_path = postcard_folder / filename
            ic("Удаляем ", file_path)
            os.remove(file_path)

        ic("Файлы удалены!")
