"""
Проверяет, у каких фильмов в базе не хватает данных. Отчёт пишется в файл.

К Кинопоиску НЕ обращается — только читает базу, поэтому лимит запросов не тратит.
Нужно, чтобы понять масштаб проблемы перед тем, как что-то дозаливать: сколько
фильмов придётся перезапросить и уложится ли это в суточный лимит API.

Главная проблема, ради которой всё затевалось, — фильм без жанров: на странице он
виден, но выпадает из любого фильтра по жанрам.

Примеры:
    uv run manage.py audit_movies                        # отчёт в movies_audit.txt
    uv run manage.py audit_movies --output /tmp/a.txt
    uv run manage.py audit_movies --daily-limit 200      # прикинуть, на сколько дней хватит
"""

from collections import Counter
from datetime import datetime
import logging
from pathlib import Path

from django.core.management.base import BaseCommand, CommandParser
from django.db.models import Count, QuerySet

from classes.movie import MISSING_RELATIONS, MovieHandler
from lists.models import Movie


logger = logging.getLogger("kinopolka")

# Что означает каждый пробел. Порядок важен — в таком виде разделы попадут в отчёт.
# Ключ соответствует коду из MISSING_LABELS (classes/movie.py).
# Значение: (заголовок, лечится ли перезапросом к API, чем это грозит)
PROBLEMS: dict[str, tuple[str, bool, str]] = {
    "genres": ("Нет жанров", True, "выпадает из фильтра по жанрам"),
    "directors": ("Нет режиссёров", True, "пропадает из статистики по людям"),
    "actors": ("Нет актёров", True, "пропадает из статистики по людям"),
    "writers": ("Нет сценаристов", True, "пропадает из статистики по людям"),
    "description": ("Пустое описание", True, "пустая карточка фильма"),
    "premiere": ("Нет даты премьеры", True, "ломает сортировку по году"),
    "duration": ("Нет длительности", True, "пустое поле в карточке"),
    "rating_kp": ("Нет оценки Кинопоиска", True, "фильм не попадёт в топы"),
    "poster": ("Постер-заглушка", False, "лечится download_posters"),
}


class Command(BaseCommand):
    help = "Ищет фильмы с недостающими данными и пишет отчёт в файл. К API не обращается."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--output", default="movies_audit.txt", help="Куда записать отчёт.")
        parser.add_argument(
            "--daily-limit",
            type=int,
            default=200,
            help="Суточный лимит запросов к API — чтобы прикинуть, за сколько дней всё дозальётся.",
        )

    def handle(self, *args, **options) -> None:
        output = Path(options["output"])
        daily_limit = options["daily_limit"]

        movies = self._movies_with_counts()
        total = movies.count()
        if not total:
            self.stdout.write(self.style.WARNING("В базе нет фильмов."))
            return

        # {kp_id: (фильм, [коды проблем])} — только проблемные
        broken: dict[int, tuple[Movie, list[str]]] = {}
        for movie in movies:
            counts = {relation: getattr(movie, f"{relation}_n") for relation in MISSING_RELATIONS}
            problems = MovieHandler.find_missing(movie, counts)
            if problems:
                broken[movie.kp_id] = (movie, problems)

        report = self._build_report(total, broken, daily_limit)
        output.write_text(report, encoding="utf-8")

        counts = Counter(code for _movie, problems in broken.values() for code in problems)
        self.stdout.write(f"Проверено фильмов: {total}, с проблемами: {len(broken)}")
        for code, (title, _needs_api, _cost) in PROBLEMS.items():
            if counts[code]:
                self.stdout.write(f"  {title}: {counts[code]}")
        self.stdout.write(self.style.SUCCESS(f"Отчёт: {output.resolve()}"))

        logger.info("audit_movies: total=%d, broken=%d, output=%s", total, len(broken), output)

    @staticmethod
    def _movies_with_counts() -> QuerySet:
        """Один запрос вместо N+1: количества связей считаем прямо в базе."""
        return Movie.mgr.annotate(
            genres_n=Count("genres", distinct=True),
            actors_n=Count("actors", distinct=True),
            directors_n=Count("directors", distinct=True),
            writers_n=Count("writers", distinct=True),
        ).order_by("name")

    @staticmethod
    def _build_report(total: int, broken: dict[int, tuple[Movie, list[str]]], daily_limit: int) -> str:
        counts = Counter(code for _movie, problems in broken.values() for code in problems)
        need_api = {kp_id for kp_id, (_m, probs) in broken.items() if any(PROBLEMS[p][1] for p in probs)}

        lines = [
            "ОТЧЁТ О НЕДОСТАЮЩИХ ДАННЫХ",
            datetime.now().strftime("%d.%m.%Y %H:%M"),
            "",
            f"Всего фильмов в базе:        {total}",
            f"Фильмов с проблемами:        {len(broken)}",
            f"Из них требуют запроса к API: {len(need_api)}",
        ]

        if need_api and daily_limit > 0:
            days = -(-len(need_api) // daily_limit)  # округление вверх
            lines.append(f"При лимите {daily_limit} запросов в сутки это {days} дн.")

        lines += ["", "СВОДКА ПО ПРОБЛЕМАМ", "-" * 60]
        for code, (title, needs_api, cost) in PROBLEMS.items():
            mark = "API" if needs_api else "   "
            lines.append(f"[{mark}] {title:<26} {counts[code]:>4}   ({cost})")

        # Дальше — списки фильмов, по одному разделу на проблему.
        for code, (title, _needs_api, cost) in PROBLEMS.items():
            affected = [(kp_id, m) for kp_id, (m, probs) in broken.items() if code in probs]
            if not affected:
                continue

            lines += ["", "", f"{title.upper()} — {len(affected)} шт. ({cost})", "-" * 60]
            for kp_id, movie in sorted(affected, key=lambda pair: pair[1].name):
                where = "архив" if movie.is_archive else "к просмотру"
                lines.append(f"  {kp_id:>9}  {movie.name[:45]:<45}  {where}")

        lines += ["", "", "ФИЛЬМЫ С НЕСКОЛЬКИМИ ПРОБЛЕМАМИ СРАЗУ", "-" * 60]
        multi = sorted(
            ((m, probs) for m, probs in broken.values() if len(probs) > 2),
            key=lambda pair: (-len(pair[1]), pair[0].name),
        )
        if multi:
            lines.append("Похоже на оборванное сохранение — такой фильм стоит перезалить целиком.")
            lines.append("")
            for movie, problems in multi:
                titles = ", ".join(PROBLEMS[p][0].lower() for p in problems)
                lines.append(f"  {movie.kp_id:>9}  {movie.name[:45]:<45}  {len(problems)}: {titles}")
        else:
            lines.append("Таких нет.")

        return "\n".join(lines) + "\n"
