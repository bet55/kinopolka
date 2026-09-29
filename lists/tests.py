# Тесты сохранения фильма и поиска пробелов в его данных.
#
# Два требования тянут в разные стороны, поэтому проверяем оба:
#   * кривая запись в ответе КП не должна уносить с собой весь фильм;
#   * настоящий сбой на середине не должен оставлять фильм-полуфабрикат
#     (виден на странице, но выпадает из фильтра по жанрам).
from unittest.mock import patch

from asgiref.sync import async_to_sync
from django.test import TestCase

from classes.movie import KPEntities, MovieHandler
from lists.models import Movie


KP_ID = 424242


def entities(genres: list[dict], persons: dict[str, list[dict]] | None = None) -> KPEntities:
    """Минимальный ответ КП после предобработки."""
    movie = {"kp_id": KP_ID, "name": "Тестовый фильм"}
    return KPEntities(movie, persons or {"actor": [], "director": [], "writer": []}, genres)


class SaveMovieTests(TestCase):
    """Сохранение фильма и его связей."""

    def test_movie_saved_with_genres(self) -> None:
        movie_model, success = MovieHandler._save_movie_to_db(entities([{"name": "ужасы"}, {"name": "драма"}]))

        self.assertTrue(success)
        self.assertEqual(sorted(g.name for g in movie_model.genres.all()), ["драма", "ужасы"])

    def test_broken_record_is_skipped_not_fatal(self) -> None:
        """Один битый жанр не должен обнулять остальные — и тем более терять фильм."""
        movie_model, success = MovieHandler._save_movie_to_db(
            entities([{"name": "ужасы"}, {"такого_поля_нет": 1}, {"name": "драма"}])
        )

        self.assertTrue(success)
        self.assertEqual(sorted(g.name for g in movie_model.genres.all()), ["драма", "ужасы"])

    def test_movie_without_persons_still_saved(self) -> None:
        """У фильма может законно не быть состава на КП — это не повод его терять."""
        movie_model, success = MovieHandler._save_movie_to_db(entities([{"name": "драма"}]))

        self.assertTrue(success)
        self.assertEqual(movie_model.actors.count(), 0)
        self.assertTrue(Movie.mgr.filter(kp_id=KP_ID).exists())


class SaveMovieAtomicityTests(TestCase):
    """Сбой после создания строки фильма откатывает её целиком."""

    def test_failure_rolls_back_whole_movie(self) -> None:
        with (
            patch.object(MovieHandler, "_build_models", side_effect=RuntimeError("бум")),
            self.assertRaises(RuntimeError),
        ):
            MovieHandler._save_movie_to_db(entities([{"name": "ужасы"}]))

        self.assertFalse(Movie.mgr.filter(kp_id=KP_ID).exists())

    def test_async_wrapper_reports_failure(self) -> None:
        """Асинхронная обёртка гасит исключение и честно возвращает (None, False)."""
        with patch.object(MovieHandler, "_build_models", side_effect=RuntimeError("бум")):
            movie_model, success = async_to_sync(MovieHandler._a_save_movie_to_db)(entities([{"name": "ужасы"}]))

        self.assertIsNone(movie_model)
        self.assertFalse(success)
        self.assertFalse(Movie.mgr.filter(kp_id=KP_ID).exists())


class DownloadContractTests(TestCase):
    """
    Что a_download отдаёт наружу. На этот ответ завязан тост «подгрузилось не всё»
    в add_movie.js, поэтому форма важна. Ответ КП подаём готовым (kp_scheme),
    чтобы не ходить в API и не тратить суточный лимит.
    """

    def _download(self, kp_scheme: dict) -> dict:
        return async_to_sync(MovieHandler.a_download)(KP_ID, kp_scheme=kp_scheme)

    def test_full_response_saves_movie(self) -> None:
        result = self._download(
            {
                "id": KP_ID,
                "name": "Тестовый фильм",
                "genres": [{"name": "ужасы"}],
                "persons": [{"id": 1, "name": "Кто-то", "enProfession": "director"}],
            }
        )

        self.assertEqual(result["movie_id"], KP_ID)
        movie = Movie.mgr.get(kp_id=KP_ID)
        self.assertEqual([g.name for g in movie.genres.all()], ["ужасы"])
        self.assertEqual(movie.directors.count(), 1)

    def test_missing_data_is_reported_but_movie_survives(self) -> None:
        """У фильма правда нет состава на КП — сохраняем и предупреждаем, а не падаем."""
        result = self._download({"id": KP_ID, "name": "Тестовый фильм", "genres": [{"name": "ужасы"}]})

        self.assertTrue(Movie.mgr.filter(kp_id=KP_ID).exists())
        self.assertIn("актёры", result["missing"])
        self.assertNotIn("жанры", result["missing"])


class FindMissingTests(TestCase):
    """Поиск пробелов — на нём держатся и отчёт audit_movies, и тост при добавлении."""

    @staticmethod
    def _saved(genres: list[dict]) -> Movie:
        """
        Фильм, прочитанный из базы. find_missing работает только с такими:
        у объекта из update_or_create premiere осталась бы строкой.
        """
        MovieHandler._save_movie_to_db(entities(genres))
        return Movie.mgr.get(kp_id=KP_ID)

    def test_empty_relations_are_reported(self) -> None:
        missing = MovieHandler.find_missing(self._saved([]))

        for code in ("genres", "actors", "directors", "writers"):
            self.assertIn(code, missing)

    def test_filled_relation_disappears_from_report(self) -> None:
        self.assertNotIn("genres", MovieHandler.find_missing(self._saved([{"name": "ужасы"}])))

    def test_counts_shortcut_matches_direct_check(self) -> None:
        """Скрипты передают готовые счётчики — результат должен совпадать с честным подсчётом."""
        movie = self._saved([{"name": "ужасы"}])
        counts = {"genres": 1, "actors": 0, "directors": 0, "writers": 0}

        self.assertEqual(MovieHandler.find_missing(movie, counts), MovieHandler.find_missing(movie))
