from collections import namedtuple
import logging

from asgiref.sync import sync_to_async
import numpy as np
import pandas as pd
import plotly
import plotly.express as px

from features.serializers import ActorSerializer, DirectorSerializer, GenreSerializer, WriterSerializer
from lists.models import Actor, Director, Genre, Writer

from .movie import MovieHandler
from .note import NoteHandler
from .postcard import PostcardHandler


logger = logging.getLogger(__name__)


class ModelsHandler:
    """Generic handler for fetching and serializing models with ManyToMany relationships to Movie."""

    # Mapping of models to their serializers and related field names
    MODEL_SERIALIZER = {
        Genre: GenreSerializer,
        Actor: ActorSerializer,
        Director: DirectorSerializer,
        Writer: WriterSerializer,
    }

    @classmethod
    @sync_to_async
    def get_all(cls, model: Genre | Actor | Director | Writer, is_archive: bool = True) -> list[dict]:
        """
        Fetch instances of the given model and serialize them.

        :param model: The Django model class (e.g., Genre, Actor).
        :param is_archive: Filter related movies by is_archive (True, False, or None for no filter).

        :returns:List of serialized data.
        """

        # Fetch queryset
        queryset = model.mgr.all()
        queryset = queryset.filter(movie__is_archive=is_archive).distinct()

        # Serialize data
        serializer = cls.MODEL_SERIALIZER[model](queryset, many=True)
        return serializer.data


class Statistic:
    """
    Класс для обработки статистики по просмотренным и ожидаемым фильмам из списков
    """

    TOP_MOVIES = 4
    USERS_COUNT = 4
    MOVIES_DISPLAY_COLUMNS = ["kp_id", "poster_local", "name"]
    Rating = namedtuple("Rating", ["top", "bot"])

    async def extract_data(self):
        """
        Загружаем из бд все нужные таблицы и кастуем их в DataFrame
        """
        postcards = await PostcardHandler.get_all_postcards()
        notes = await NoteHandler.get_all_notes("list")
        genres = await ModelsHandler.get_all(Genre)
        actors = await ModelsHandler.get_all(Actor)
        writers = await ModelsHandler.get_all(Writer)
        directors = await ModelsHandler.get_all(Director)

        archive_movies = await MovieHandler.get_all_movies("rating", is_archive=True)
        movies = await MovieHandler.get_all_movies("rating")

        self.postcards = pd.DataFrame(postcards)
        self.notes = pd.DataFrame(notes)
        self.genres = pd.DataFrame(genres)
        self.actors = pd.DataFrame(actors)
        self.writers = pd.DataFrame(writers)
        self.directors = pd.DataFrame(directors)

        self.archive_movies = pd.DataFrame(archive_movies)
        self.movies = pd.DataFrame(movies)

        # почему-то слетают типы
        wrong_types = ["duration", "rating_kp", "rating_imdb"]
        self.archive_movies.loc[:, wrong_types] = self.archive_movies.loc[:, wrong_types].astype(np.float16)

    async def genres(self):
        return 11

    async def _get_movies_rated_by_all_users(self) -> pd.DataFrame:
        notes = self.notes

        rate_counts = notes.groupby(["movie"]).size().reset_index().rename(columns={0: "count"})
        movies_rated_by_all_users = rate_counts[rate_counts["count"] == self.USERS_COUNT]["movie"].tolist()

        notes = notes[notes.movie.isin(movies_rated_by_all_users)]
        return notes

    async def _get_movies_by_imdb_rating(self) -> Rating:
        """
        Самые лучшие и худшие фильмы по оценкам на imdb
        """
        df = self.archive_movies
        df["rating_imdb"] = df["rating_imdb"].astype(float)
        df = df.rename(columns={"rating_imdb": "rating"})
        return self._get_top_and_bot_rated_movies(df)

    async def _get_movies_by_kinopolka_rating(self) -> Rating:
        """
        Самые лучшие и худшие фильмы по оценкам на кинополке
        """
        df = await self._get_movies_rated_by_all_users()
        df = df.rename(columns={"movie": "kp_id"})
        return self._get_top_and_bot_rated_movies(df)

    def _get_top_and_bot_rated_movies(self, df: pd.DataFrame) -> Rating:
        """
        Получаем фильмы с самой высокой и самой низкой оценкой
        """
        agg_by_rating = (
            df.groupby(["kp_id"])
            .agg({"rating": "mean"})
            .reset_index()
            .sort_values(by="rating", ascending=False)
            .round(1)
        )

        # какие поля нужны для отображения
        display_movies = self.archive_movies[self.MOVIES_DISPLAY_COLUMNS]

        top_movies = agg_by_rating.head(self.TOP_MOVIES)
        bot_movies = agg_by_rating.tail(self.TOP_MOVIES)

        top_movies = pd.merge(top_movies, display_movies, on="kp_id").to_dict(orient="records")
        bot_movies = pd.merge(bot_movies, display_movies, on="kp_id").to_dict(orient="records")

        return self.Rating(top=top_movies, bot=bot_movies)

    async def outstanding_actors(self) -> dict[str : list[dict]]:
        """
        Собираем актёров с лучшими и худшими оценками фильмов по разным агрегаторам
        """
        return {
            "Топ рейтинг на imdb": [],
            "Топ рейтинг на кинополке": [],
            "Бот рейтинг на imdb": [],
            "Бот рейтинг на кинополке": [],
        }

    async def outstanding_directors(self) -> dict[str : list[dict]]:
        pass

    async def outstanding_genres(self) -> str:
        df = self.genres.loc[:, ["name", "movies_count"]]
        df = df.sort_values(by="movies_count", ascending=False)

        # Берём топ-5 и редкие 5 жанров
        common_genres = df.head(5).reset_index(drop=True)
        rare_genres = df.tail(5).reset_index(drop=True)

        # Создаём DataFrame с MultiIndex напрямую
        result_df = pd.DataFrame(
            {
                ("Популярные", "жанр"): common_genres["name"],
                ("Популярные", "фильмов"): common_genres["movies_count"],
                ("Редкие", "жанр"): rare_genres["name"],
                ("Редкие", "фильмов"): rare_genres["movies_count"],
            }
        )

        # Генерируем HTML (Pandas сам сделает colspan)
        return result_df.to_html(index=False, classes="genres-table", border=0, justify="center")

    async def outstanding_movies(self) -> dict[str : list[dict]]:
        """
        Собираем фильмы с лучшими и худшими оценками по разным агрегаторам
        """
        kinopolka_movies = await self._get_movies_by_kinopolka_rating()
        imdb_movies = await self._get_movies_by_imdb_rating()

        return {
            "Топ рейтинг на imdb": imdb_movies.top,
            "Топ рейтинг на кинополке": kinopolka_movies.top,
            "Бот рейтинг на imdb": imdb_movies.bot,
            "Бот рейтинг на кинополке": kinopolka_movies.bot,
        }

    async def statistic(self):
        """
        Базовая статистика по таблице с фильмами
        """
        df = pd.DataFrame(self.archive_movies)

        notes = pd.DataFrame(self.notes)
        users_mean_rating = notes.groupby(["movie"]).agg({"rating": "mean"}).rating.mean().round(2)

        postcards = self.postcards
        meetings_count = len(postcards[postcards["is_active"] == False])

        stats = {
            "Общая продолжительность": df["duration"].sum(),
            "Количество собраний": meetings_count,
            "Средняя оценка на кинопоиске": df["rating_kp"].mean().round(2),
            "Средняя оценка на imdb": df["rating_imdb"].mean().round(2),
            "Средняя оценка на кинополке": users_mean_rating,
            "Посмотрено фильмов": len(df),
            "Фильмов на просмотр": len(self.movies),
        }

        return stats

    async def most_popular_persons(self):
        return []

    async def draw(self):
        film_model = await MovieHandler.get_all_movies(is_archive=True)
        film_model = film_model.values()

        df = pd.DataFrame(film_model)
        figure_config = {
            "x": "rating_kp",
            "width": 800,
            "color_discrete_sequence": ["#9bab6e"],
            "labels": {
                "rating_kp": "Средняя оценка пользователей",
                "count": "Количество оценок",
            },
        }
        figure = px.histogram(df, **figure_config)
        graph_div = plotly.offline.plot(figure, auto_open=False, output_type="div")

        return graph_div
