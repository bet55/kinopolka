from classes.exceptions import MoviesError
from classes.note import Note
from classes.kp import KP_Movie
from lists.models import Film as FilmModel, Actor as ActorModel, Writer as WriterModel, Director as DirectorModel, \
    Genre as GenreModel
from lists.serializers import FilmSerializer, FilmSmallSerializer
from pydantic_models import KPFilmModel, KpFilmPersonModel, KpFilmGenresModel
from collections import namedtuple


class MovieHandler:
    KPEntities = namedtuple('KPEntities', ['movie', 'persons', 'genres'])

    @classmethod
    def get_movie(cls, kp_id: int | str) -> dict:
        film_model = FilmModel.mgr.get(kp_id=kp_id)
        serialize = FilmSerializer(film_model)
        return serialize.data

    @classmethod
    def get_all_movies(cls, all_info: bool = True, is_archive: bool = False) -> dict | list:
        try:
            raw_film = FilmModel.mgr.filter(is_archive=is_archive)
            serialize = FilmSerializer(raw_film, many=True) if all_info else FilmSmallSerializer(raw_film, many=True)
            return serialize.data
        except:
            raise MoviesError

    @classmethod
    def change_movie_status(cls, kp_id: int | str, is_archive: bool):
        film_model = FilmModel.mgr.get(kp_id=kp_id)
        film_model.is_archive = is_archive
        return film_model.save()

    @classmethod
    def remove_movie(cls, kp_id: int | str):
        film_model = FilmModel.mgr.get(kp_id=kp_id)
        return film_model.delete()

    @classmethod
    def download(cls, kp_id: int | str) -> tuple[int, bool]:

        kp_client = KP_Movie()
        api_response = kp_client.get_movie_by_id(kp_id)

        converted_response = cls._response_preprocess(api_response)

        save_movies = cls._save_movie_to_db(converted_response)

        return api_response.get('id', -1), save_movies[1]

    @classmethod
    def _save_movie_to_db(cls, movie_info: KPEntities):
        movie, persons, genres = movie_info

        movie_model, m_status = FilmModel.mgr.update_or_create(**movie)

        a, d, w, g = cls._create_models_counstuctor_list(persons, genres)
        ActorModel.mgr.bulk_create(a, update_conflicts=True, update_fields=['photo'], unique_fields=['kp_id'])
        DirectorModel.mgr.bulk_create(d, update_conflicts=True, update_fields=['photo'], unique_fields=['kp_id'])
        WriterModel.mgr.bulk_create(w, update_conflicts=True, update_fields=['photo'], unique_fields=['kp_id'])
        GenreModel.mgr.bulk_create(g, update_conflicts=True, update_fields=['watch_counter'], unique_fields=['name'])

        movie_model.actors.set(a)
        movie_model.directors.set(d)
        movie_model.writers.set(w)
        movie_model.genres.set(g)

        return movie_model, m_status

    @classmethod
    async def a_download(cls, kp_id: int | str, kp_scheme: dict = None) -> tuple[int, bool]:

        if not kp_scheme:
            kp_client = KP_Movie()
            api_response = kp_client.get_movie_by_id(kp_id)
        else:
            api_response = kp_scheme

        converted_response = cls._response_preprocess(api_response)

        save_movies = await cls._a_save_movie_to_db(converted_response)

        return api_response.get('id', -1), save_movies[1]

    @classmethod
    async def _a_save_movie_to_db(cls, movie_info: KPEntities):
        movie, persons, genres = movie_info
        movie_model, m_status = await FilmModel.mgr.aupdate_or_create(**movie)

        a, d, w, g = cls._create_models_counstuctor_list(persons, genres)

        await ActorModel.mgr.abulk_create(a, update_conflicts=True, update_fields=['photo'], unique_fields=['kp_id'])
        await DirectorModel.mgr.abulk_create(d, update_conflicts=True, update_fields=['photo'], unique_fields=['kp_id'])
        await WriterModel.mgr.abulk_create(w, update_conflicts=True, update_fields=['photo'], unique_fields=['kp_id'])
        await GenreModel.mgr.abulk_create(g, update_conflicts=True, update_fields=['watch_counter'],
                                          unique_fields=['name'])

        await movie_model.actors.aset(a)
        await movie_model.directors.aset(d)
        await movie_model.writers.aset(w)
        await movie_model.genres.aset(g)

        return movie_model, m_status

    @classmethod
    def _create_models_counstuctor_list(cls, persons: dict[str, list], genres: list) -> tuple[list, list, list, list]:
        actors = [ActorModel(**pers) for pers in persons['actor']]
        directors = [DirectorModel(**pers) for pers in persons['director']]
        writers = [WriterModel(**pers) for pers in persons['writer']]
        genres = [GenreModel(**gen) for gen in genres]

        return actors, directors, writers, genres

    @classmethod
    def _response_preprocess(cls, movie_info: dict) -> KPEntities:

        movie = cls._movie_preprocess(movie_info)
        persons = cls._persons_preprocess(movie_info)
        genres = cls._genres_preprocess(movie_info)

        return cls.KPEntities(movie, persons, genres)

    @classmethod
    def _genres_preprocess(cls, movie_info: dict) -> list[str]:
        modeling = KpFilmGenresModel(genres=movie_info.get('genres'))
        formated_genres = modeling.dict().get('genres')
        return formated_genres

    @classmethod
    def _movie_preprocess(cls, movie_info: dict) -> dict[str, int | str]:
        modeling = KPFilmModel(**movie_info)
        formated_movie = modeling.model_dump(exclude_none=True, exclude_defaults=True, exclude_unset=True)
        return formated_movie

    @classmethod
    def _persons_preprocess(cls, movie_info: dict) -> dict[str, list]:
        persons = {'actor': [], 'writer': [], 'director': []}

        for p in movie_info.get('persons', []):
            if not all([p.get('id'), p.get('name')]):
                continue

            try:
                persons[p['enProfession']].append(
                    KpFilmPersonModel(**p).model_dump(exclude_none=True, exclude_defaults=True, exclude_unset=True))
            except KeyError:
                continue

        return persons
