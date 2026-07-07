"""
Обновляет "живую" статистику у недавно вышедших фильмов.

Когда фильм добавляется на сайт, его данные фиксируются на момент добавления и
больше не обновляются. Для свежих фильмов оценки KP/IMDb, число голосов и кассовые
сборы со временем заметно меняются. Эта команда находит фильмы с премьерой за
последние N лет, заново запрашивает их у Кинопоиска и обновляет ТОЛЬКО эти поля.

Остальные поля (название, описание, постер, watch_date, is_archive, оценки клуба и
т.д.) не трогаются — сохраняются через save(update_fields=...).

Примеры:
    uv run manage.py update_recent_movies                 # премьеры за 2 года
    uv run manage.py update_recent_movies --years 3
    uv run manage.py update_recent_movies --dry-run       # показать, но не сохранять
    uv run manage.py update_recent_movies --limit 5 --delay 2
"""

from datetime import timedelta
import logging
import time

from django.core.management.base import BaseCommand, CommandParser
from django.utils import timezone
from pydantic import ValidationError as PydanticValidationError

from classes.kp import KP_Movie
from lists.models import Movie
from pydantic_models import KPFilmModel


logger = logging.getLogger("kinopolka")

# Поля, которые могут измениться со временем и которые обновляем.
DECIMAL_FIELDS = ("rating_kp", "rating_imdb")
INT_FIELDS = ("votes_kp", "votes_imdb", "fees")
VOLATILE_FIELDS = DECIMAL_FIELDS + INT_FIELDS


class Command(BaseCommand):
    help = "Обновляет оценки KP/IMDb, число голосов и кассовые сборы у фильмов с премьерой за последние N лет."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--years", type=int, default=2, help="За сколько последних лет брать фильмы (по премьере).")
        parser.add_argument("--delay", type=float, default=1.0, help="Пауза между запросами к API, сек.")
        parser.add_argument("--limit", type=int, default=0, help="Ограничить число фильмов (0 — без ограничения).")
        parser.add_argument("--dry-run", action="store_true", help="Показать изменения, но не сохранять.")

    def handle(self, *args, **options) -> None:
        years = options["years"]
        delay = options["delay"]
        limit = options["limit"]
        dry_run = options["dry_run"]

        cutoff = timezone.now() - timedelta(days=365 * years)
        movies = Movie.mgr.filter(premiere__gte=cutoff).order_by("-premiere")
        if limit:
            movies = movies[:limit]

        total = len(movies)
        self.stdout.write(f"Фильмов с премьерой за последние {years} г.: {total}" + (" (dry-run)" if dry_run else ""))
        if not total:
            return

        kp = KP_Movie()
        updated = unchanged = errors = 0

        for i, movie in enumerate(movies, 1):
            prefix = f"[{i}/{total}] {movie.kp_id} {movie.name}"

            api_response = kp.get_movie_by_id(movie.kp_id)
            if not api_response:
                self.stdout.write(self.style.WARNING(f"{prefix}: нет данных ({kp.error})"))
                errors += 1
                time.sleep(delay)
                continue

            try:
                parsed = KPFilmModel(**api_response)
            except PydanticValidationError as e:
                self.stdout.write(self.style.ERROR(f"{prefix}: ошибка разбора ({e})"))
                errors += 1
                time.sleep(delay)
                continue

            changes = self._collect_changes(movie, parsed)
            if not changes:
                unchanged += 1
                time.sleep(delay)
                continue

            for field, (_old, new) in changes.items():
                setattr(movie, field, new)

            diff = ", ".join(f"{f}: {o}→{n}" for f, (o, n) in changes.items())
            if not dry_run:
                movie.save(update_fields=list(changes.keys()))
            self.stdout.write(f"{prefix}: {diff}")
            updated += 1
            time.sleep(delay)

        action = "будет обновлено" if dry_run else "обновлено"
        self.stdout.write(
            self.style.SUCCESS(f"Готово. {action}: {updated}, без изменений: {unchanged}, ошибок: {errors}")
        )
        logger.info(
            "update_recent_movies: %s=%d, unchanged=%d, errors=%d, years=%d, dry_run=%s",
            action,
            updated,
            unchanged,
            errors,
            years,
            dry_run,
        )

    @staticmethod
    def _collect_changes(movie: Movie, parsed: KPFilmModel) -> dict[str, tuple]:
        """
        Сравнивает волатильные поля модели и свежего ответа API.
        Возвращает {поле: (старое, новое)} только для реально изменившихся полей.
        Пустые/нулевые значения из API игнорируются, чтобы не затирать корректные данные.
        """
        changes: dict[str, tuple] = {}
        for field in VOLATILE_FIELDS:
            new = getattr(parsed, field)
            if not new:  # API вернул 0/None — не понижаем существующие данные до нуля
                continue

            old = getattr(movie, field)
            if field in DECIMAL_FIELDS:
                if round(float(old), 3) != round(float(new), 3):
                    changes[field] = (old, new)
            elif int(old) != int(new):
                changes[field] = (old, new)
        return changes
