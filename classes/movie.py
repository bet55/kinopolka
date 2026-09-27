import asyncio
import logging
from typing import NamedTuple

from asgiref.sync import sync_to_async
from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models import Model
import httpx
from pydantic import ValidationError as PydanticValidationError
from rest_framework.exceptions import ValidationError

from classes.kp import KP_Movie
from features.serializers import MovieRatingSerializer
from lists.models import QUESTION_MARK_URL, Actor, Director, Genre, Movie, Writer
from lists.serializers import MovieDictSerializer, MoviePosterSerializer
from pydantic_models import KpFilmGenresModel, KPFilmModel, KpFilmPersonModel
from utils.exception_handler import handle_exceptions


# Configure logger
logger = logging.getLogger(__name__)


class MoviesStructure:
    posters = "posters"
    rating = "rating"


class KPEntities(NamedTuple):
    movie: dict[str, int | str]
    persons: dict[str, list[dict]]
    genres: list[dict]


# Данные, которых у фильма может не оказаться. Код → как назвать это человеку.
# Часть полей пустует законно (у фильма правда нет постера на Кинопоиске), поэтому
# это повод предупредить, а не повод отказаться сохранять фильм.
MISSING_LABELS: dict[str, str] = {
    "genres": "жанры",
    "directors": "режиссёры",
    "actors": "актёры",
    "writers": "сценаристы",
    "description": "описание",
    "premiere": "дата премьеры",
    "duration": "длительность",
    "rating_kp": "оценка Кинопоиска",
    "poster": "постер",
}

# Связи и скалярные поля проверяются по-разному, поэтому разделены.
MISSING_RELATIONS = ("genres", "directors", "actors", "writers")

DEFAULT_PREMIERE_YEAR = 1900
DEFAULT_TEXTS = frozenset({"...", "", "Без описания", "Таинственный фильм без названия"})
DEFAULT_POSTER_LOCAL = "media/posters/default.png"


class MovieHandler:
    """
    Класс для работы с фильмами в базе данных.
    """

    @classmethod
    @handle_exceptions("Фильм")
    @sync_to_async
    def get_movie(cls, kp_id: int | str) -> dict:
        """
        Получение фильма по Kinopoisk ID.
        :param kp_id: Kinopoisk ID фильма (целое число или строка).
        :return: Сериализованные данные фильма.
        """
        if not kp_id or not isinstance(kp_id, (int, str)) or (isinstance(kp_id, int) and kp_id <= 0):
            raise ValidationError("Некорректный kp_id", 400)

        film_model = Movie.mgr.get(kp_id=kp_id)
        return MovieDictSerializer(film_model).data

    @classmethod
    @handle_exceptions("Фильмы")
    @sync_to_async
    def get_all_movies(cls, info_type: str | None = None, is_archive: bool = False) -> list[dict]:
        """
        Получение всех фильмов с фильтрацией по статусу архива и типом сериализации.
        :param info_type: Тип сериализации (posters, rating или None для полных данных).
        :param is_archive: Фильтрация по архивным фильмам.
        :return: Список сериализованных фильмов.
        """
        raw_films = Movie.mgr.filter(is_archive=is_archive)

        # prefetch под конкретный сериализатор, иначе N+1: жанры и заметки
        # дёргаются отдельным запросом на каждый фильм
        if info_type == MoviesStructure.posters:
            raw_films = raw_films.prefetch_related("genres", "note_set")
        elif info_type != MoviesStructure.rating:
            raw_films = raw_films.prefetch_related("genres")

        serialisers = {MoviesStructure.posters: MoviePosterSerializer, MoviesStructure.rating: MovieRatingSerializer}
        serializer = serialisers.get(info_type, MovieDictSerializer)
        movies = serializer(raw_films, many=True).data

        logger.info(
            "Получено %d фильмов (is_archive=%s, info_type=%s)",
            len(movies),
            is_archive,
            info_type,
        )
        return movies

    @classmethod
    @handle_exceptions("Фильм")
    async def change_movie_status(cls, kp_id: int | str, is_archive: bool) -> bool:
        """
        Обновление статуса архива фильма.
        :param kp_id: Kinopoisk ID фильма.
        :param is_archive: Новый статус архива (True для архива, False для активного).
        :return: True если обновление успешно.
        """
        if not kp_id or not isinstance(kp_id, (int, str)) or (isinstance(kp_id, int) and kp_id <= 0):
            raise ValidationError("Некорректный kp_id", 400)
        if not isinstance(is_archive, bool):
            raise ValidationError("Некорректное значение is_archive", 400)

        film_model = await Movie.mgr.aget(kp_id=kp_id)
        film_model.is_archive = is_archive
        await film_model.asave()
        logger.info("Обновлен статус архива для фильма %s на %s", kp_id, is_archive)
        return True

    @classmethod
    @handle_exceptions("Фильм")
    async def remove_movie(cls, kp_id: int | str) -> bool:
        """
        Удаление фильма по Kinopoisk ID.
        :param kp_id: Kinopoisk ID фильма.
        :return: True если удаление успешно.
        """
        if not kp_id or not isinstance(kp_id, (int, str)) or (isinstance(kp_id, int) and kp_id <= 0):
            raise ValidationError("Некорректный kp_id", 400)

        film_model = await Movie.mgr.aget(kp_id=kp_id)
        await film_model.adelete()
        logger.info("Удален фильм с kp_id: %s", kp_id)
        return True

    @classmethod
    @handle_exceptions("Фильм")
    async def a_download(cls, kp_id: int | str, kp_scheme: dict | None = None) -> dict:
        """
        Асинхронная загрузка данных фильма из Kinopoisk API и сохранение в базу данных.
        :param kp_id: Kinopoisk ID фильма.
        :param kp_scheme: Опциональный ответ API. Если None, данные запрашиваются из API.
        :return: {"movie_id": id, "missing": [человекочитаемые названия пустых полей]}.
            Неполные данные — не ошибка: у фильма может правда не быть постера или
            состава на Кинопоиске. Фильм сохраняем, а о пробелах предупреждаем.
        """
        if not kp_id or not isinstance(kp_id, (int, str)) or (isinstance(kp_id, int) and kp_id <= 0):
            raise ValidationError("Некорректный kp_id", 400)

        movie = await cls.get_movie(kp_id=kp_id)

        if not movie.get("error"):
            raise ValidationError("Фильм уже существует", 400)

        kp_client = KP_Movie()
        # запрос к API синхронный (httpx.Client) — уводим в поток, чтобы не блокировать event loop
        api_response = kp_scheme if kp_scheme else await asyncio.to_thread(kp_client.get_movie_by_id, kp_id)
        if not api_response:
            raise ValidationError("Данные не получены из Kinopoisk API", 500)

        movie_info = cls._response_preprocess(api_response)
        movie_model, success = await cls._a_save_movie_to_db(movie_info)
        if not success:
            raise ValidationError("Не удалось сохранить фильм в базу данных", 520)

        if api_response.get("poster", {}).get("url"):
            await cls._download_and_save_poster(movie_model, api_response["poster"]["url"], kp_id)

        # Перечитываем: у объекта из update_or_create поля держат то, что в них
        # положили (premiere — строка из ответа КП), типы Django приводит только
        # при чтении из базы. find_missing ждёт нормальную модель.
        await movie_model.arefresh_from_db()
        missing = await sync_to_async(cls.find_missing, thread_sensitive=True)(movie_model)
        if missing:
            logger.warning("Фильм %s сохранён с пробелами: %s", kp_id, ", ".join(missing))

        logger.info("Асинхронно загружен и сохранен фильм %s: success=%s", kp_id, success)
        return {
            "movie_id": api_response.get("id", -1),
            "missing": [MISSING_LABELS[code] for code in missing],
        }

    @classmethod
    async def _download_and_save_poster(cls, movie_model: Movie, poster_url: str, kp_id: str) -> bool:
        """
        Асинхронная загрузка и сохранение постера фильма.
        """
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(poster_url)
                response.raise_for_status()

                file_name = f"poster_{kp_id}.jpg"
                content_file = ContentFile(response.content)

                save_file = sync_to_async(movie_model.poster_local.save, thread_sensitive=True)
                await save_file(file_name, content_file, save=True)

                logger.info("Загружен и сохранен постер для фильма %s", kp_id)
                return True
        except Exception as e:
            logger.error("Не удалось загрузить постер для фильма %s: %s", kp_id, str(e))
            movie_model.poster_local = None
            await movie_model.asave()
            return False

    @classmethod
    async def _a_save_movie_to_db(cls, movie_info: KPEntities) -> tuple[Movie | None, bool]:
        """
        Асинхронное сохранение данных фильма в базу данных.
        Обёртка над синхронным `_save_movie_to_db`: транзакция должна жить внутри
        одного потока, поэтому весь блок уводим в sync_to_async целиком, а не
        дёргаем ORM по одному await-у.
        """
        try:
            return await sync_to_async(cls._save_movie_to_db, thread_sensitive=True)(movie_info)
        except Exception as e:
            logger.error("Не удалось асинхронно сохранить фильм: %s", str(e))
            return None, False

    @classmethod
    @transaction.atomic
    def _save_movie_to_db(cls, movie_info: KPEntities) -> tuple[Movie, bool]:
        """
        Сохранение фильма и всех его связей одной транзакцией.

        Без atomic сбой на середине (таймаут API, кривая персона в ответе) оставлял
        в базе строку фильма без жанров и персон: на сайте он виден, но выпадает
        из фильтра по жанрам. Теперь либо сохраняется всё, либо ничего.
        """
        movie, persons, genres = movie_info
        movie_model, _ = Movie.mgr.update_or_create(**movie)

        actors, directors, writers, genres = cls._create_models_constructor_list(persons, genres)
        Actor.mgr.bulk_create(
            actors,
            update_conflicts=True,
            update_fields=["photo"],
            unique_fields=["kp_id"],
        )
        Director.mgr.bulk_create(
            directors,
            update_conflicts=True,
            update_fields=["photo"],
            unique_fields=["kp_id"],
        )
        Writer.mgr.bulk_create(
            writers,
            update_conflicts=True,
            update_fields=["photo"],
            unique_fields=["kp_id"],
        )
        Genre.mgr.bulk_create(
            genres,
            update_conflicts=True,
            update_fields=["watch_counter"],
            unique_fields=["name"],
        )

        movie_model.actors.set(actors)
        movie_model.directors.set(directors)
        movie_model.writers.set(writers)
        movie_model.genres.set(genres)

        logger.debug("Сохранен фильм: kp_id=%s", movie.get("kp_id"))
        return movie_model, True

    @classmethod
    def _create_models_constructor_list(
        cls, persons: dict[str, list[dict]], genres: list[dict]
    ) -> tuple[list[Actor], list[Director], list[Writer], list[Genre]]:
        """
        Создание экземпляров моделей для актеров, режиссеров, сценаристов и жанров.

        Раньше любая осечка возвращала четыре пустых списка разом — фильм сохранялся
        вообще без связей и выпадал из фильтра по жанрам. Теперь кривая запись
        отбрасывается поштучно: один битый актёр не уносит с собой жанры.
        """
        actors = cls._build_models(Actor, persons.get("actor", []))
        directors = cls._build_models(Director, persons.get("director", []))
        writers = cls._build_models(Writer, persons.get("writer", []))
        genre_models = cls._build_models(Genre, genres)

        logger.debug(
            "Создано %d актеров, %d режиссеров, %d сценаристов, %d жанров",
            len(actors),
            len(directors),
            len(writers),
            len(genre_models),
        )
        return actors, directors, writers, genre_models

    @staticmethod
    def _build_models(model: type[Model], raw_items: list[dict]) -> list[Model]:
        """
        Собирает модели по одной. Запись, которую не удалось разобрать, пропускается
        с записью в лог — остальные сохраняются.
        """
        built = []
        for item in raw_items:
            try:
                built.append(model(**item))
            except Exception as e:
                logger.warning("Пропущена запись %s (%s): %s", model.__name__, item, e)
        return built

    @classmethod
    def _response_preprocess(cls, movie_info: dict) -> KPEntities:
        """
        Предобработка ответа API Kinopoisk.
        """
        movie = cls._movie_preprocess(movie_info)
        persons = cls._persons_preprocess(movie_info)
        genres = cls._genres_preprocess(movie_info)
        logger.debug("Предобработан ответ API для фильма: kp_id=%s", movie.get("kp_id"))
        return KPEntities(movie, persons, genres)

    @classmethod
    def _movie_preprocess(cls, movie_info: dict) -> dict[str, int | str]:
        """
        Предобработка данных фильма из ответа API.
        """
        try:
            modeling = KPFilmModel(**movie_info)
            formatted_movie = modeling.model_dump(exclude_none=True, exclude_defaults=True, exclude_unset=True)
            logger.debug("Предобработаны данные фильма: kp_id=%s", formatted_movie.get("kp_id"))
            return formatted_movie
        except PydanticValidationError as e:
            logger.warning("Некорректные данные фильма: %s", str(e))
            raise ValidationError("Некорректные данные фильма") from e
        except Exception as e:
            logger.error("Неожиданная ошибка при предобработке фильма: %s", str(e))
            raise ValidationError("Ошибка при предобработке фильма") from e

    @classmethod
    def _persons_preprocess(cls, movie_info: dict) -> dict[str, list[dict]]:
        """
        Предобработка данных персон из ответа API.
        """

        try:
            persons = {"actor": [], "director": [], "writer": []}
            for person in movie_info.get("persons", []):
                if not all([person.get("id"), person.get("name")]):
                    logger.debug("Пропущена персона с отсутствующим id или именем: %s", person)
                    continue
                try:
                    # Get profession and normalize it
                    profession = person.get("enProfession", "").lower()

                    # Skip if not one of our target professions
                    if profession not in persons:
                        continue

                    persons[profession].append(
                        KpFilmPersonModel(**person).model_dump(
                            exclude_none=True, exclude_defaults=True, exclude_unset=True
                        )
                    )
                except (KeyError, PydanticValidationError):
                    logger.debug("Пропущена некорректная персона: %s", person)
                    continue
            logger.debug(
                "Предобработано %d актеров, %d режиссеров, %d сценаристов",
                len(persons["actor"]),
                len(persons["director"]),
                len(persons["writer"]),
            )
            return persons
        except Exception as e:
            logger.error("Не удалось предобработать персон: %s", str(e))
            raise ValidationError("Ошибка при предобработке персон") from e

    @classmethod
    def _genres_preprocess(cls, movie_info: dict) -> list[dict]:
        """
        Предобработка данных жанров из ответа API.
        """
        try:
            modeling = KpFilmGenresModel(genres=movie_info.get("genres", []))
            formatted_genres = modeling.dict().get("genres", [])
            logger.debug("Предобработано %d жанров", len(formatted_genres))
            return formatted_genres
        except PydanticValidationError as e:
            logger.warning("Некорректные данные жанров: %s", str(e))
            raise ValidationError("Некорректные данные жанров") from e
        except Exception as e:
            logger.error("Неожиданная ошибка при предобработке жанров: %s", str(e))
            raise ValidationError("Ошибка при предобработке жанров") from e

    @classmethod
    def extract_genres(cls, movies: list[dict]) -> list[str]:
        """
        Получение списка уникальных жанров из переданных фильмов.
        :param movies: Список фильмов, содержащий поле "genres".
        :return: Список уникальных жанров.
        """
        genres = []
        for movie in movies:
            genres += movie.get("genres", [])
        return sorted(list(set(genres)))

    @classmethod
    def find_missing(cls, movie: Movie, counts: dict[str, int] | None = None) -> list[str]:
        """
        Коды незаполненных данных фильма — ключи MISSING_LABELS.

        :param movie: Фильм, **прочитанный из базы**. У объекта, только что созданного
            в памяти, поля держат то, что в них положили: например, premiere будет
            строкой, а не датой. Django приводит типы только на границе с базой.
        :param counts: Заранее посчитанные размеры связей {"genres": 3, ...}.
            Нужны скриптам, которые пробегают всю базу: без них на каждый фильм
            уйдёт по запросу на связь.
        :return: Список кодов, пустой если всё на месте.
        """
        missing = []

        for relation in MISSING_RELATIONS:
            amount = counts[relation] if counts else getattr(movie, relation).count()
            if not amount:
                missing.append(relation)

        if (movie.description or "").strip() in DEFAULT_TEXTS:
            missing.append("description")

        if movie.premiere.year <= DEFAULT_PREMIERE_YEAR:
            missing.append("premiere")
        if not movie.duration:
            missing.append("duration")
        if not movie.rating_kp:
            missing.append("rating_kp")

        poster_local = str(movie.poster_local or "")
        if movie.poster == QUESTION_MARK_URL or not poster_local or DEFAULT_POSTER_LOCAL in poster_local:
            missing.append("poster")

        return missing
