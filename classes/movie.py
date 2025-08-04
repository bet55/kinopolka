import logging
from typing import Dict, List, NamedTuple, Optional, Tuple, Union

import httpx
from asgiref.sync import sync_to_async
from django.core.files.base import ContentFile
from rest_framework.exceptions import ValidationError

from classes.kp import KP_Movie
from lists.models import Actor, Director, Genre, Movie, Writer
from lists.serializers import (
    MovieDictSerializer,
    MoviePosterSerializer
)
from features.serializers import MovieRatingSerializer
from pydantic_models import KpFilmGenresModel, KPFilmModel, KpFilmPersonModel
from utils.exception_handler import handle_exceptions

# Configure logger
logger = logging.getLogger(__name__)


class MoviesStructure:
    posters = "posters"
    rating = "rating"


class KPEntities(NamedTuple):
    movie: Dict[str, Union[int, str]]
    persons: Dict[str, List[Dict]]
    genres: List[Dict]


class MovieHandler:
    """
    Класс для работы с фильмами в базе данных.
    """

    @classmethod
    @handle_exceptions("Фильм")
    @sync_to_async
    def get_movie(cls, kp_id: Union[int, str]) -> dict:
        """
        Получение фильма по Kinopoisk ID.
        :param kp_id: Kinopoisk ID фильма (целое число или строка).
        :return: Сериализованные данные фильма.
        """
        if (
            not kp_id
            or not isinstance(kp_id, (int, str))
            or (isinstance(kp_id, int) and kp_id <= 0)
        ):
            raise ValidationError("Некорректный kp_id", 400)

        film_model = Movie.mgr.get(kp_id=kp_id)
        return MovieDictSerializer(film_model).data

    @classmethod
    @handle_exceptions("Фильмы")
    @sync_to_async
    def get_all_movies(
        cls, info_type: Optional[str] = None, is_archive: bool = False
    ) -> List[dict]:
        """
        Получение всех фильмов с фильтрацией по статусу архива и типом сериализации.
        :param info_type: Тип сериализации (posters, rating или None для полных данных).
        :param is_archive: Фильтрация по архивным фильмам.
        :return: Список сериализованных фильмов.
        """
        raw_films = Movie.mgr.filter(is_archive=is_archive)

        if info_type == MoviesStructure.posters:
            serializer = MoviePosterSerializer(raw_films, many=True)
        elif info_type == MoviesStructure.rating:
            serializer = MovieRatingSerializer(raw_films, many=True)
        else:
            serializer = MovieDictSerializer(raw_films, many=True)

        logger.info(
            "Получено %d фильмов (is_archive=%s, info_type=%s)",
            raw_films.count(),
            is_archive,
            info_type,
        )
        return serializer.data

    @classmethod
    @handle_exceptions("Фильм")
    async def change_movie_status(
        cls, kp_id: Union[int, str], is_archive: bool
    ) -> bool:
        """
        Обновление статуса архива фильма.
        :param kp_id: Kinopoisk ID фильма.
        :param is_archive: Новый статус архива (True для архива, False для активного).
        :return: True если обновление успешно.
        """
        if (
            not kp_id
            or not isinstance(kp_id, (int, str))
            or (isinstance(kp_id, int) and kp_id <= 0)
        ):
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
    async def remove_movie(cls, kp_id: Union[int, str]) -> bool:
        """
        Удаление фильма по Kinopoisk ID.
        :param kp_id: Kinopoisk ID фильма.
        :return: True если удаление успешно.
        """
        if (
            not kp_id
            or not isinstance(kp_id, (int, str))
            or (isinstance(kp_id, int) and kp_id <= 0)
        ):
            raise ValidationError("Некорректный kp_id", 400)

        film_model = await Movie.mgr.aget(kp_id=kp_id)
        await film_model.adelete()
        logger.info("Удален фильм с kp_id: %s", kp_id)
        return True

    @classmethod
    @handle_exceptions("Фильм")
    async def a_download(
        cls, kp_id: Union[int, str], kp_scheme: Optional[Dict] = None
    ) -> int:
        """
        Асинхронная загрузка данных фильма из Kinopoisk API и сохранение в базу данных.
        :param kp_id: Kinopoisk ID фильма.
        :param kp_scheme: Опциональный ответ API. Если None, данные запрашиваются из API.
        :return: Кортеж (movie_id, успех).
        """
        if (
            not kp_id
            or not isinstance(kp_id, (int, str))
            or (isinstance(kp_id, int) and kp_id <= 0)
        ):
            raise ValidationError("Некорректный kp_id", 400)

        movie = await cls.get_movie(kp_id=kp_id)


        if not movie.get('error'):
            raise ValidationError("Фильм уже существует", 400)

        kp_client = KP_Movie()
        api_response = kp_scheme if kp_scheme else kp_client.get_movie_by_id(kp_id)
        if not api_response:
            raise ValidationError("Данные не получены из Kinopoisk API", 500)

        movie_info = cls._response_preprocess(api_response)
        movie_model, success = await cls._a_save_movie_to_db(movie_info)
        if not success:
            raise ValidationError("Не удалось сохранить фильм в базу данных", 520)

        if api_response.get("poster", {}).get("url"):
            await cls._download_and_save_poster(
                movie_model, api_response["poster"]["url"], kp_id
            )

        logger.info(
            "Асинхронно загружен и сохранен фильм %s: success=%s", kp_id, success
        )
        return api_response.get("id", -1)

    @classmethod
    async def _download_and_save_poster(
        cls, movie_model: Movie, poster_url: str, kp_id: str
    ) -> bool:
        """
        Асинхронная загрузка и сохранение постера фильма.
        """
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(poster_url)
                response.raise_for_status()

                file_name = f"poster_{kp_id}.jpg"
                content_file = ContentFile(response.content)

                save_file = sync_to_async(
                    movie_model.poster_local.save, thread_sensitive=True
                )
                await save_file(file_name, content_file, save=True)

                logger.info("Загружен и сохранен постер для фильма %s", kp_id)
                return True
        except Exception as e:
            logger.error("Не удалось загрузить постер для фильма %s: %s", kp_id, str(e))
            movie_model.poster_local = None
            await movie_model.asave()
            return False

    @classmethod
    async def _a_save_movie_to_db(
        cls, movie_info: KPEntities
    ) -> Tuple[Optional[Movie], bool]:
        """
        Асинхронное сохранение данных фильма в базу данных.
        """
        try:
            movie, persons, genres = movie_info
            movie_model, _ = await Movie.mgr.aupdate_or_create(**movie)

            actors, directors, writers, genres = cls._create_models_constructor_list(
                persons, genres
            )
            await Actor.mgr.abulk_create(
                actors,
                update_conflicts=True,
                update_fields=["photo"],
                unique_fields=["kp_id"],
            )
            await Director.mgr.abulk_create(
                directors,
                update_conflicts=True,
                update_fields=["photo"],
                unique_fields=["kp_id"],
            )
            await Writer.mgr.abulk_create(
                writers,
                update_conflicts=True,
                update_fields=["photo"],
                unique_fields=["kp_id"],
            )
            await Genre.mgr.abulk_create(
                genres,
                update_conflicts=True,
                update_fields=["watch_counter"],
                unique_fields=["name"],
            )

            await movie_model.actors.aset(actors)
            await movie_model.directors.aset(directors)
            await movie_model.writers.aset(writers)
            await movie_model.genres.aset(genres)

            logger.debug("Асинхронно сохранен фильм: kp_id=%s", movie.get("kp_id"))
            return movie_model, True
        except Exception as e:
            logger.error("Не удалось асинхронно сохранить фильм: %s", str(e))
            return None, False

    @classmethod
    def _create_models_constructor_list(
        cls, persons: Dict[str, List[Dict]], genres: List[Dict]
    ) -> Tuple[List[Actor], List[Director], List[Writer], List[Genre]]:
        """
        Создание экземпляров моделей для актеров, режиссеров, сценаристов и жанров.
        """
        try:
            actors = [Actor(**pers) for pers in persons.get("actor", [])]
            directors = [Director(**pers) for pers in persons.get("director", [])]
            writers = [Writer(**pers) for pers in persons.get("writer", [])]
            genres = [Genre(**gen) for gen in genres]
            logger.debug(
                "Создано %d актеров, %d режиссеров, %d сценаристов, %d жанров",
                len(actors),
                len(directors),
                len(writers),
                len(genres),
            )
            return actors, directors, writers, genres
        except Exception as e:
            logger.error("Не удалось создать экземпляры моделей: %s", str(e))
            return [], [], [], []

    @classmethod
    def _response_preprocess(cls, movie_info: Dict) -> KPEntities:
        """
        Предобработка ответа API Kinopoisk.
        """
        movie = cls._movie_preprocess(movie_info)
        persons = cls._persons_preprocess(movie_info)
        genres = cls._genres_preprocess(movie_info)
        logger.debug("Предобработан ответ API для фильма: kp_id=%s", movie.get("kp_id"))
        return KPEntities(movie, persons, genres)

    @classmethod
    def _movie_preprocess(cls, movie_info: Dict) -> Dict[str, Union[int, str]]:
        """
        Предобработка данных фильма из ответа API.
        """
        try:
            modeling = KPFilmModel(**movie_info)
            formatted_movie = modeling.model_dump(
                exclude_none=True, exclude_defaults=True, exclude_unset=True
            )
            logger.debug(
                "Предобработаны данные фильма: kp_id=%s", formatted_movie.get("kp_id")
            )
            return formatted_movie
        except KPFilmModel.ValidationError as e:
            logger.warning("Некорректные данные фильма: %s", str(e))
            raise ValidationError("Некорректные данные фильма")
        except Exception as e:
            logger.error("Неожиданная ошибка при предобработке фильма: %s", str(e))
            raise ValidationError("Ошибка при предобработке фильма")

    @classmethod
    def _persons_preprocess(cls, movie_info: Dict) -> Dict[str, List[Dict]]:
        """
        Предобработка данных персон из ответа API.
        """

        try:
            persons = {"actor": [], "director": [], "writer": []}
            for person in movie_info.get("persons", []):
                if not all([person.get("id"), person.get("name")]):
                    logger.debug(
                        "Пропущена персона с отсутствующим id или именем: %s", person
                    )
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
                except (KeyError, KpFilmPersonModel.ValidationError):
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
            raise ValidationError("Ошибка при предобработке персон")

    @classmethod
    def _genres_preprocess(cls, movie_info: Dict) -> List[Dict]:
        """
        Предобработка данных жанров из ответа API.
        """
        try:
            modeling = KpFilmGenresModel(genres=movie_info.get("genres", []))
            formatted_genres = modeling.dict().get("genres", [])
            logger.debug("Предобработано %d жанров", len(formatted_genres))
            return formatted_genres
        except KpFilmGenresModel.ValidationError as e:
            logger.warning("Некорректные данные жанров: %s", str(e))
            raise ValidationError("Некорректные данные жанров")
        except Exception as e:
            logger.error("Неожиданная ошибка при предобработке жанров: %s", str(e))
            raise ValidationError("Ошибка при предобработке жанров")

    @classmethod
    def extract_genres(cls, movies: List[Dict]) -> List[str]:
        """
        Получение списка уникальных жанров из переданных фильмов.
        :param movies: Список фильмов, содержащий поле "genres".
        :return: Список уникальных жанров.
        """
        genres = []
        for movie in movies:
            genres += movie.get("genres", [])
        return list(set(genres))
