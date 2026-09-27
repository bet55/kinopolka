"""
Дозаливает фильмам недостающие данные: жанры, персон, пустые поля карточки.

Что заполнять — определяет тот же `MovieHandler.find_missing`, по которому строит
отчёт `audit_movies`. Сначала посмотри отчёт, потом запускай это.

Трогает ТОЛЬКО то, чего не хватает: непустые поля, оценки клуба, watch_date и
is_archive не перезаписываются. Каждый фильм сохраняется своей транзакцией —
сбой на одном не рушит остальные.

Каждый фильм — один запрос к API, так что следи за суточным лимитом: ограничивай
через --limit. Нужен `source env.sh` перед запуском, иначе «Missing API key».

Примеры:
    source env.sh
    uv run manage.py fill_missing_data --dry-run             # только показать
    uv run manage.py fill_missing_data --only genres         # самое дешёвое
    uv run manage.py fill_missing_data --limit 150 --delay 1
"""

import logging
import time

from django.core.management.base import BaseCommand, CommandParser
from django.db import transaction
from django.db.models import Count, QuerySet

from classes.kp import KP_Movie
from classes.movie import MISSING_LABELS, MISSING_RELATIONS, KPEntities, MovieHandler
from lists.models import Actor, Director, Genre, Movie, Writer


logger = logging.getLogger("kinopolka")

# Связь → (модель, ключ в предобработанных персонах). У жанров своя ветка ответа.
RELATION_MODELS = {
    "genres": (Genre, None),
    "actors": (Actor, "actor"),
    "directors": (Director, "director"),
    "writers": (Writer, "writer"),
}

# Скалярные поля, которые умеем дозаполнять. Постер сюда не входит — им занимается
# download_posters, отдельной командой.
SCALAR_FIELDS = ("description", "premiere", "duration", "rating_kp")

FILLABLE = set(RELATION_MODELS) | set(SCALAR_FIELDS)


class Command(BaseCommand):
    help = "Дозаливает фильмам недостающие жанры, персон и пустые поля. Каждый фильм — один запрос к API."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--only",
            nargs="+",
            choices=sorted(FILLABLE),
            help="Заполнять только указанное (например: --only genres). По умолчанию — всё.",
        )
        parser.add_argument("--limit", type=int, default=0, help="Не больше N фильмов за запуск (0 — без лимита).")
        parser.add_argument("--delay", type=float, default=1.0, help="Пауза между запросами к API, сек.")
        parser.add_argument("--retries", type=int, default=2, help="Сколько раз повторить неудавшийся запрос.")
        parser.add_argument("--dry-run", action="store_true", help="Показать, что будет заполнено, но не сохранять.")

    def handle(self, *args, **options) -> None:
        wanted = set(options["only"]) if options["only"] else FILLABLE
        limit = options["limit"]
        delay = options["delay"]
        retries = options["retries"]
        dry_run = options["dry_run"]

        targets = self._collect_targets(wanted)
        if limit:
            targets = targets[:limit]

        total = len(targets)
        suffix = " (dry-run)" if dry_run else ""
        self.stdout.write(f"Фильмов к дозаливке: {total}{suffix}")
        if not total:
            self.stdout.write(self.style.SUCCESS("Заполнять нечего."))
            return

        kp = KP_Movie()
        filled = errors = 0

        for i, (movie, missing) in enumerate(targets, 1):
            prefix = f"[{i}/{total}] {movie.kp_id} {movie.name}"
            names = ", ".join(MISSING_LABELS[code] for code in missing)

            # dry-run не ходит в API вообще: суточный лимит слишком дорог,
            # чтобы тратить его на предпросмотр
            if dry_run:
                self.stdout.write(f"{prefix}: будет запрошено — {names}")
                filled += 1
                continue

            api_response = self._fetch(kp, movie.kp_id, retries, delay)
            if not api_response:
                self.stdout.write(self.style.WARNING(f"{prefix}: нет данных ({kp.error})"))
                errors += 1
                continue

            try:
                entities = MovieHandler._response_preprocess(api_response)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"{prefix}: ошибка разбора ({e})"))
                errors += 1
                time.sleep(delay)
                continue

            try:
                done = self._fill(movie, missing, entities)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"{prefix}: не удалось сохранить ({e})"))
                errors += 1
                time.sleep(delay)
                continue

            if done:
                self.stdout.write(f"{prefix}: заполнено — {', '.join(MISSING_LABELS[c] for c in done)}")
                filled += 1
            else:
                # У фильма правда нет этих данных на Кинопоиске — повторять бессмысленно.
                self.stdout.write(self.style.WARNING(f"{prefix}: на Кинопоиске тоже пусто ({names})"))

            time.sleep(delay)

        action = "будет заполнено" if dry_run else "заполнено"
        self.stdout.write(self.style.SUCCESS(f"Готово. {action}: {filled}, ошибок: {errors}"))
        logger.info("fill_missing_data: %s=%d, errors=%d, dry_run=%s", action, filled, errors, dry_run)

    @staticmethod
    def _collect_targets(wanted: set[str]) -> list[tuple[Movie, list[str]]]:
        """Фильмы, которым есть что дозалить, вместе со списком кодов пробелов."""
        movies: QuerySet = Movie.mgr.annotate(
            genres_n=Count("genres", distinct=True),
            actors_n=Count("actors", distinct=True),
            directors_n=Count("directors", distinct=True),
            writers_n=Count("writers", distinct=True),
        ).order_by("name")

        targets = []
        for movie in movies:
            counts = {relation: getattr(movie, f"{relation}_n") for relation in MISSING_RELATIONS}
            missing = [code for code in MovieHandler.find_missing(movie, counts) if code in wanted]
            if missing:
                targets.append((movie, missing))
        return targets

    def _fetch(self, kp: KP_Movie, kp_id: int, retries: int, delay: float) -> dict | None:
        """Запрос к API с повтором: сеть иногда моргает, а лимит тратить жалко."""
        for attempt in range(retries + 1):
            api_response = kp.get_movie_by_id(kp_id)
            if api_response:
                return api_response

            if attempt < retries:
                self.stdout.write(f"    повтор {attempt + 1}/{retries} для {kp_id} ({kp.error})")
                time.sleep(delay)
        return None

    @staticmethod
    @transaction.atomic
    def _fill(movie: Movie, missing: list[str], entities: KPEntities) -> list[str]:
        """
        Заполняет пробелы фильма. Возвращает коды того, что реально удалось заполнить:
        если на Кинопоиске данных тоже нет, список будет короче запрошенного.
        """
        movie_fields, persons, genres = entities
        done = []

        for code in missing:
            if code not in RELATION_MODELS:
                continue

            model, persons_key = RELATION_MODELS[code]
            raw = genres if persons_key is None else persons.get(persons_key, [])
            objects = MovieHandler._build_models(model, raw)
            if not objects:
                continue

            unique_field = "name" if model is Genre else "kp_id"
            update_field = "watch_counter" if model is Genre else "photo"
            model.mgr.bulk_create(
                objects,
                update_conflicts=True,
                update_fields=[update_field],
                unique_fields=[unique_field],
            )
            getattr(movie, code).set(objects)
            done.append(code)

        changed_fields = []
        for code in missing:
            if code not in SCALAR_FIELDS:
                continue

            value = movie_fields.get(code)
            if value in (None, "", 0):
                continue

            setattr(movie, code, value)
            changed_fields.append(code)
            done.append(code)

        if changed_fields:
            movie.save(update_fields=changed_fields)

        return done
