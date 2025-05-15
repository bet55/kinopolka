import logging
from typing import Dict, List, Optional, Tuple, Union, NamedTuple
from enum import Enum
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import IntegrityError
from django.core.files.base import ContentFile
import httpx
from lists.models import Movie, Actor, Director, Writer, Genre
from lists.serializers import MovieDictSerializer, MoviePosterSerializer, MovieRatingSerializer
from pydantic_models import KPFilmModel, KpFilmPersonModel, KpFilmGenresModel
from classes.kp import KP_Movie
from asgiref.sync import sync_to_async

# Configure logger
logger = logging.getLogger('kinopolka')


class MoviesStructure(Enum):
    posters = "posters"
    rating = "rating"


class KPEntities(NamedTuple):
    movie: Dict[str, Union[int, str]]
    persons: Dict[str, List[Dict]]
    genres: List[Dict]


class MovieHandler:
    """
    Класс для работы с фильмами в базе данных
    """
    @classmethod
    def extract_genres(cls, movies: List[Dict]):
        """
        Получаем список уникальных жанров у переданных фильмов
        :param movies: Список фильмов, содержащий поле "genres"
        :return: list
        """

        genres = []
        for movie in movies:
            genres += movie.get('genres', [])
        return list(set(genres))

    @classmethod
    @sync_to_async
    def get_movie(cls, kp_id: Union[int, str]) -> Optional[Dict]:
        """
        Retrieve a movie by its Kinopoisk ID.

        Args:
            kp_id: Kinopoisk ID of the movie (integer or string).

        Returns:
            Serialized movie data as a dictionary, or None if the movie is not found or an error occurs.
        """
        if not kp_id or not isinstance(kp_id, (int, str)) or (isinstance(kp_id, int) and kp_id <= 0):
            logger.error("Invalid kp_id: %s", kp_id)
            return None

        try:
            film_model = Movie.mgr.get(kp_id=kp_id) # aget не работает ))))))))
            serialized = MovieDictSerializer(film_model)
            logger.info("Retrieved movie with kp_id: %s", kp_id)
            return serialized.data

        except (ObjectDoesNotExist, MultipleObjectsReturned) as e:
            logger.warning("Failed to retrieve movie %s: %s", kp_id, str(e))
            return None
        except Exception as e:
            logger.error("Unexpected error retrieving movie %s: %s", kp_id, str(e))
            return None

    @classmethod
    @sync_to_async
    def get_all_movies(
            cls, info_type: Optional[MoviesStructure] = None, is_archive: bool = False
    ) -> List[Dict]:
        """
        Retrieve all movies, optionally filtered by archive status and serialized by type.

        Args:
            info_type: Type of serialization (posters, rating, or None for full data). Defaults to None.
            is_archive: Whether to retrieve archived movies. Defaults to False.

        Returns:
            List of serialized movie data dictionaries, or an empty list if no movies are found or an error occurs.
        """
        try:
            raw_films = Movie.mgr.filter(is_archive=is_archive)

            if info_type == MoviesStructure.posters.value:
                logger.debug("Serializing movies with MovieSmallSerializer")
                serializer = MoviePosterSerializer(raw_films, many=True)
            elif info_type == MoviesStructure.rating.value:
                logger.debug("Serializing movies with MovieRatingSerializer")
                serializer = MovieRatingSerializer(raw_films, many=True)
            else:
                logger.debug("Serializing movies with MovieSerializer")
                serializer = MovieDictSerializer(raw_films, many=True)

            logger.info("Retrieved %d movies (is_archive=%s, info_type=%s)", raw_films.count(), is_archive, info_type)
            return serializer.data

        except Exception as e:
            logger.error("Failed to retrieve movies: %s", str(e))
            return []

    @classmethod
    async def change_movie_status(cls, kp_id: Union[int, str], is_archive: bool) -> bool:
        """
        Update the archive status of a movie.

        Args:
            kp_id: Kinopoisk ID of the movie (integer or string).
            is_archive: New archive status (True for archived, False for active).

        Returns:
            True if the status was updated successfully, False if the movie was not found or an error occurred.
        """
        if not kp_id or not isinstance(kp_id, (int, str)) or (isinstance(kp_id, int) and kp_id <= 0):
            logger.error("Invalid kp_id: %s", kp_id)
            return False

        if not isinstance(is_archive, bool):
            logger.error("Invalid is_archive: %s", is_archive)
            return False

        try:
            film_model = await Movie.mgr.aget(kp_id=kp_id)
            film_model.is_archive = is_archive
            await film_model.asave()
            logger.info("Updated archive status for movie %s to %s", kp_id, is_archive)
            return True

        except (ObjectDoesNotExist, MultipleObjectsReturned) as e:
            logger.warning("Failed to update movie %s status: %s", kp_id, str(e))
            return False
        except Exception as e:
            logger.error("Unexpected error updating movie %s status: %s", kp_id, str(e))
            return False

    @classmethod
    async def remove_movie(cls, kp_id: Union[int, str]) -> bool:
        """
        Delete a movie by its Kinopoisk ID.

        Args:
            kp_id: Kinopoisk ID of the movie (integer or string).

        Returns:
            True if the movie was deleted successfully, False if the movie was not found or an error occurred.
        """
        if not kp_id or not isinstance(kp_id, (int, str)) or (isinstance(kp_id, int) and kp_id <= 0):
            logger.error("Invalid kp_id: %s", kp_id)
            return False

        try:
            film_model = await Movie.mgr.aget(kp_id=kp_id)
            await film_model.adelete()
            logger.info("Deleted movie with kp_id: %s", kp_id)
            return True

        except (ObjectDoesNotExist, MultipleObjectsReturned) as e:
            logger.warning("Failed to delete movie %s: %s", kp_id, str(e))
            return False
        except Exception as e:
            logger.error("Unexpected error deleting movie %s: %s", kp_id, str(e))
            return False

    @classmethod
    def download(cls, kp_id: Union[int, str]) -> Tuple[int, bool]:
        """
        Download movie data from Kinopoisk API and save it to the database.

        Args:
            kp_id: Kinopoisk ID of the movie (integer or string).

        Returns:
            Tuple of (movie ID, success status). Returns (-1, False) if an error occurs.
        """
        if not kp_id or not isinstance(kp_id, (int, str)) or (isinstance(kp_id, int) and kp_id <= 0):
            logger.error("Invalid kp_id: %s", kp_id)
            return -1, False

        try:
            kp_client = KP_Movie()
            api_response = kp_client.get_movie_by_id(kp_id)
            if not api_response:
                logger.warning("No data returned from KP API for kp_id: %s", kp_id)
                return -1, False

            converted_response = cls._response_preprocess(api_response)
            movie_model, success = cls._save_movie_to_db(converted_response)
            logger.info("Downloaded and saved movie %s: success=%s", kp_id, success)
            return api_response.get("id", -1), success

        except Exception as e:
            logger.error("Failed to download movie %s: %s", kp_id, str(e))
            return -1, False

    @classmethod
    async def a_download(cls, kp_id: Union[int, str], kp_scheme: Optional[Dict] = None) -> Tuple[int, bool]:
        """
        Asynchronously download movie data from Kinopoisk API or provided scheme and save it to the database.

        Args:
            kp_id: Kinopoisk ID of the movie (integer or string).
            kp_scheme: Optional pre-fetched API response dictionary. If None, fetches from API.

        Returns:
            Tuple of (movie ID, success status). Returns (-1, False) if an error occurs.
        """
        if not kp_id or not isinstance(kp_id, (int, str)) or (isinstance(kp_id, int) and kp_id <= 0):
            logger.error("Invalid kp_id: %s", kp_id)
            return -1, False

        try:
            if not kp_scheme:
                kp_client = KP_Movie()
                api_response = kp_client.get_movie_by_id(kp_id)
                if not api_response:
                    logger.warning("No data returned from KP API for kp_id: %s", kp_id)
                    return -1, False
            else:
                api_response = kp_scheme

            converted_response = cls._response_preprocess(api_response)
            movie_model, success = await cls._a_save_movie_to_db(converted_response)

            if success and api_response.get("poster", {}).get("url"):
                await cls._download_and_save_poster(movie_model, api_response["poster"]["url"], kp_id)

            logger.info("Asynchronously downloaded and saved movie %s: success=%s", kp_id, success)
            return api_response.get("id", -1), success

        except Exception as e:
            logger.error("Failed to asynchronously download movie %s: %s", kp_id, str(e))
            return -1, False

    @classmethod
    async def _download_and_save_poster(cls, movie_model: Movie, poster_url: str, kp_id: str) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(poster_url)
                response.raise_for_status()
                file_name = f"poster_{kp_id}.jpg"
                movie_model.poster_local.save(file_name, ContentFile(response.content), save=True)
                logger.info("Downloaded and saved poster for movie %s", kp_id)
                return True
        except Exception as e:
            logger.error("Failed to download poster for movie %s: %s", kp_id, str(e))
            movie_model.poster_local = None #default value
            await movie_model.asave()
            return False

    @classmethod
    def _save_movie_to_db(cls, movie_info: KPEntities) -> Tuple[Movie, bool]:
        """
        Save movie data to the database (synchronous).

        Args:
            movie_info: KPEntities tuple containing movie, persons, and genres data.

        Returns:
            Tuple of (Movie model instance, success status). Returns (None, False) if an error occurs.
        """
        try:
            movie, persons, genres = movie_info
            movie_model, m_status = Movie.mgr.update_or_create(**movie)

            actors, directors, writers, genres = cls._create_models_constructor_list(persons, genres)
            Actor.mgr.bulk_create(
                actors, update_conflicts=True, update_fields=["photo"], unique_fields=["kp_id"]
            )
            Director.mgr.bulk_create(
                directors, update_conflicts=True, update_fields=["photo"], unique_fields=["kp_id"]
            )
            Writer.mgr.bulk_create(
                writers, update_conflicts=True, update_fields=["photo"], unique_fields=["kp_id"]
            )
            Genre.mgr.bulk_create(
                genres, update_conflicts=True, update_fields=["watch_counter"], unique_fields=["name"]
            )

            movie_model.actors.set(actors)
            movie_model.directors.set(directors)
            movie_model.writers.set(writers)
            movie_model.genres.set(genres)

            logger.debug("Saved movie to database: kp_id=%s, status=%s", movie.get("kp_id"), m_status)
            return movie_model, True

        except (IntegrityError, Exception) as e:
            logger.error("Failed to save movie to database: %s", str(e))
            return None, False

    @classmethod
    async def _a_save_movie_to_db(cls, movie_info: KPEntities) -> Tuple[Optional[Movie], bool]:
        """
        Asynchronously save movie data to the database.

        Args:
            movie_info: KPEntities tuple containing movie, persons, and genres data.

        Returns:
            Tuple of (Movie model instance, success status). Returns (None, False) if an error occurs.
        """
        try:
            movie, persons, genres = movie_info
            movie_model, m_status = await Movie.mgr.aupdate_or_create(**movie)

            actors, directors, writers, genres = cls._create_models_constructor_list(persons, genres)
            await Actor.mgr.abulk_create(
                actors, update_conflicts=True, update_fields=["photo"], unique_fields=["kp_id"]
            )
            await Director.mgr.abulk_create(
                directors, update_conflicts=True, update_fields=["photo"], unique_fields=["kp_id"]
            )
            await Writer.mgr.abulk_create(
                writers, update_conflicts=True, update_fields=["photo"], unique_fields=["kp_id"]
            )
            await Genre.mgr.abulk_create(
                genres, update_conflicts=True, update_fields=["watch_counter"], unique_fields=["name"]
            )

            await movie_model.actors.aset(actors)
            await movie_model.directors.aset(directors)
            await movie_model.writers.aset(writers)
            await movie_model.genres.aset(genres)

            logger.debug("Asynchronously saved movie to database: kp_id=%s, status=%s", movie.get("kp_id"), m_status)
            return movie_model, True

        except (IntegrityError, Exception) as e:
            logger.error("Failed to asynchronously save movie to database: %s", str(e))
            return None, False

    @classmethod
    def _create_models_constructor_list(
            cls, persons: Dict[str, List[Dict]], genres: List[Dict]
    ) -> Tuple[List[Actor], List[Director], List[Writer], List[Genre]]:
        """
        Create model instances for actors, directors, writers, and genres.

        Args:
            persons: Dictionary mapping roles (actor, director, writer) to lists of person data.
            genres: List of genre data dictionaries.

        Returns:
            Tuple of lists containing Actor, Director, Writer, and Genre model instances.
        """
        try:
            actors = [Actor(**pers) for pers in persons.get("actor", [])]
            directors = [Director(**pers) for pers in persons.get("director", [])]
            writers = [Writer(**pers) for pers in persons.get("writer", [])]
            genres = [Genre(**gen) for gen in genres]
            logger.debug("Created %d actors, %d directors, %d writers, %d genres",
                         len(actors), len(directors), len(writers), len(genres))
            return actors, directors, writers, genres

        except Exception as e:
            logger.error("Failed to create model instances: %s", str(e))
            return [], [], [], []

    @classmethod
    def _response_preprocess(cls, movie_info: Dict) -> Optional[KPEntities]:
        """
        Preprocess Kinopoisk API response into KPEntities.

        Args:
            movie_info: Raw API response dictionary.

        Returns:
            KPEntities tuple (movie, persons, genres), or None if preprocessing fails.
        """
        try:
            movie = cls._movie_preprocess(movie_info)
            persons = cls._persons_preprocess(movie_info)
            genres = cls._genres_preprocess(movie_info)
            logger.debug("Preprocessed API response for movie: kp_id=%s", movie.get("kp_id"))
            return KPEntities(movie, persons, genres)

        except Exception as e:
            logger.error("Failed to preprocess API response: %s", str(e))
            return None

    @classmethod
    def _movie_preprocess(cls, movie_info: Dict) -> Dict[str, Union[int, str]]:
        """
        Preprocess movie data from API response.

        Args:
            movie_info: Raw API response dictionary.

        Returns:
            Formatted movie data dictionary, or empty dict if preprocessing fails.
        """
        try:
            modeling = KPFilmModel(**movie_info)
            formatted_movie = modeling.model_dump(
                exclude_none=True, exclude_defaults=True, exclude_unset=True
            )
            logger.debug("Preprocessed movie data: kp_id=%s", formatted_movie.get("kp_id"))
            return formatted_movie

        except KPFilmModel.ValidationError as e:
            logger.warning("Invalid movie data: %s", str(e))
            return {}
        except Exception as e:
            logger.error("Unexpected error preprocessing movie: %s", str(e))
            return {}

    @classmethod
    def _persons_preprocess(cls, movie_info: Dict) -> Dict[str, List[Dict]]:
        """
        Preprocess persons data from API response.

        Args:
            movie_info: Raw API response dictionary.

        Returns:
            Dictionary mapping roles (actor, director, writer) to lists of person data, or empty dict if preprocessing fails.
        """
        try:
            persons = {"actor": [], "director": [], "writer": []}
            for person in movie_info.get("persons", []):
                if not all([person.get("id"), person.get("name")]):
                    logger.debug("Skipping person with missing id or name: %s", person)
                    continue

                try:
                    persons[person["enProfession"]].append(
                        KpFilmPersonModel(**person).model_dump(
                            exclude_none=True, exclude_defaults=True, exclude_unset=True
                        )
                    )
                except (KeyError, KpFilmPersonModel.ValidationError):
                    logger.debug("Skipping invalid person: %s", person)
                    continue

            logger.debug("Preprocessed %d actors, %d directors, %d writers",
                         len(persons["actor"]), len(persons["director"]), len(persons["writer"]))
            return persons

        except Exception as e:
            logger.error("Failed to preprocess persons: %s", str(e))
            return {"actor": [], "director": [], "writer": []}

    @classmethod
    def _genres_preprocess(cls, movie_info: Dict) -> List[Dict]:
        """
        Preprocess genres data from API response.

        Args:
            movie_info: Raw API response dictionary.

        Returns:
            List of formatted genre data dictionaries, or empty list if preprocessing fails.
        """
        try:
            modeling = KpFilmGenresModel(genres=movie_info.get("genres", []))
            formatted_genres = modeling.dict().get("genres", [])
            logger.debug("Preprocessed %d genres", len(formatted_genres))
            return formatted_genres

        except KpFilmGenresModel.ValidationError as e:
            logger.warning("Invalid genres data: %s", str(e))
            return []
        except Exception as e:
            logger.error("Unexpected error preprocessing genres: %s", str(e))
            return []
