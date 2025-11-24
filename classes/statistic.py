from collections import namedtuple
import logging

from asgiref.sync import sync_to_async
import numpy as np
import pandas as pd
import plotly
import plotly.express as px

from features.serializers import ActorSerializer, DirectorSerializer, GenreSerializer, WriterSerializer
from lists.models import Actor, Director, Genre, Writer

from .movie import MovieHandler, MoviesStructure
from .note import NoteHandler
from .postcard import PostcardHandler
from .user import UserHandler

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
    def get_all(cls, model: Genre | Actor | Director | Writer, is_archive: bool = True) -> pd.DataFrame:
        """
        Fetch instances of the given model and serialize them.

        :param model: The Django model class (e.g., Genre, Actor).
        :param is_archive: Filter related movies by is_archive (True, False, or None for no filter).

        :returns:List of serialized data.
        """
        queryset = model.mgr.all()
        queryset = queryset.filter(movie__is_archive=is_archive).distinct()

        # Serialize data
        serializer = cls.MODEL_SERIALIZER[model](queryset, many=True)
        return pd.DataFrame(serializer.data)


class Statistic:
    """
    Класс для обработки статистики по просмотренным и ожидаемым фильмам из списков
    """

    TOP_MOVIES = 4
    TOP_PERSONS = 5  # writers, actors, directors
    USERS_COUNT = 4
    MOVIES_DISPLAY_COLUMNS = ["kp_id", "poster_local", "name"]
    RATING_PLATFORMS = 11
    Rating = namedtuple("Rating", ["top", "bot"])

    async def extract_data(self):
        """
        Загружаем из бд все нужные таблицы и кастуем их в DataFrame
        """
        archive_movies = await MovieHandler.get_all_movies("rating", is_archive=True)
        notes = await NoteHandler.get_all_notes("list")

        # формат dataframe
        genres = await ModelsHandler.get_all(Genre)
        notes = pd.DataFrame(notes)
        archive_movies = pd.DataFrame(archive_movies)

        # Невероятные приключения с исправлением типа для рейтинга.
        # Скорее всего из-за запятых - 3,5 вместо 3.5
        wrong_types = ["rating_kp", "rating_imdb"]
        archive_movies[wrong_types] = archive_movies[wrong_types].replace(',', '.', regex=True)
        archive_movies[wrong_types] = archive_movies[wrong_types].astype(np.float64).round(2)

        # добавляем наши оценки фильмов
        polka = notes.groupby('movie', as_index=False).agg({'rating': 'mean', 'user': 'count'}).round(1)
        archive_movies = pd.merge(archive_movies, polka, left_on="kp_id", right_on="movie", how="inner")

        self.archive_movies = archive_movies
        self.notes = notes
        self.genres = genres.sort_values(by="movies_count", ascending=False)

    def _get_top_and_bot_rated_movies(self, rating_type: str) -> Rating:
        """
        Получаем фильмы с самой высокой и самой низкой оценкой
        :param rating_type: какой рейтинг считаем - ratin, rating_imdb, rating_kp
        :return: Rating
        """
        movies = self.archive_movies.copy()

        if rating_type == 'rating':
            movies = movies[movies.user == self.USERS_COUNT]

        movies = movies.sort_values(by=rating_type, ascending=False)

        top_movies = movies.head(self.TOP_MOVIES).to_dict(orient='records')
        bot_movies = movies.tail(self.TOP_MOVIES).to_dict(orient='records')

        return self.Rating(top=top_movies, bot=bot_movies)

    async def users(self) -> pd.DataFrame:
        users = await UserHandler.get_all_users()

    async def outstanding_actors(self) -> pd.DataFrame:
        actors = await ModelsHandler.get_all(Actor)
        return actors[actors['movies_count'] == self.TOP_PERSONS]

    async def outstanding_directors(self) -> pd.DataFrame:
        directors = await ModelsHandler.get_all(Director)
        return directors[directors['movies_count'] == self.TOP_PERSONS]

    async def outstanding_writers(self) -> pd.DataFrame:
        writers = await ModelsHandler.get_all(Writer)
        return writers[writers['movies_count'] == self.TOP_PERSONS]

    async def outstanding_genres(self) -> str:
        """
        Получаем самые частые и самые редкие жанры
        """

        common_genres = self.genres.head(5).reset_index(drop=True)
        rare_genres = self.genres.tail(5).reset_index(drop=True)

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

    async def outstanding_movies(self) -> dict[str: list[dict]]:
        """
        Собираем фильмы с лучшими и худшими оценками по разным агрегаторам
        """

        kinopolka_movies = self._get_top_and_bot_rated_movies('rating')
        imdb_movies = self._get_top_and_bot_rated_movies('rating_imdb')
        kp_movies = self._get_top_and_bot_rated_movies('rating_kp')

        return {
            "imdb": imdb_movies,
            "kp": kp_movies,
            "kinopolka": kinopolka_movies
        }


    async def statistic(self) -> dict[str: int | float]:
        """
        Базовая статистика по таблице с фильмами
        """
        movies = await MovieHandler.get_all_movies(MoviesStructure.rating)
        postcards = await PostcardHandler.get_all_postcards()

        df = self.archive_movies
        users_mean_rating = df.rating.mean().round(2)

        stats = {
            "Общая продолжительность": df["duration"].sum(),
            "Количество собраний": len(postcards),
            "Средняя оценка на кинопоиске": df["rating_kp"].mean().round(2),
            "Средняя оценка на imdb": df["rating_imdb"].mean().round(2),
            "Средняя оценка на кинополке": users_mean_rating,
            "Посмотрено фильмов": len(df),
            "Фильмов на просмотр": len(movies),
        }

        return stats


    async def draw(self) -> dict[str, str]:
        """
        Возвращает 5 крутых графиков в виде HTML-div
        """

        am = self.archive_movies.copy()
        notes = self.notes

        # 1. Распределение оценок Кинополки
        fig1 = px.histogram(
            notes,
            x="rating",
            nbins=10,
            title="Распределение оценок на Кинополке",
            labels={"rating": "Оценки кинополки", "count": "Количество фильмов"},
            color_discrete_sequence=["#e67e22"],
            template="simple_white",
        )
        fig1.update_layout(bargap=0.1, title_x=0.5, font_size=14)

        # 2. Наши оценки vs IMDb — главная фишка кинопоики!
        am["diff"] = round(am["rating"] - am["rating_imdb"], 2)
        am = am.dropna()

        fig2 = px.scatter(
            am,
            x="rating_imdb",
            y="rating",
            hover_name="name",
            title="Мы vs Мир: где мы добрее/суровее IMDb",
            labels={"rating": "Оценка кинопоикой", "rating_imdb": "IMDb"},
            color="diff",
            color_continuous_scale=["#e74c3c", "#95a5a6", "#27ae60"],
            range_x=[5, 10],
            range_y=[4, 10],
        )
        fig2.add_shape(type="line", line=dict(dash="dash", color="#34495e"), x0=5, x1=10, y0=5, y1=10)
        fig2.update_layout(title_x=0.5, coloraxis_colorbar=dict(title="Мы - IMDb"))

        # 3. Топ-10 переоценённых и недооценённых нами фильмов
        top_overrated = am.nlargest(10, "diff")[["name", "rating_imdb", "rating", "diff"]]
        top_underrated = am.nsmallest(10, "diff")[["name", "rating_imdb", "rating", "diff"]]

        fig3 = px.bar(
            top_overrated,
            x="diff",
            y="name",
            orientation="h",
            title="Топ-10 переоценённых нами фильмов",
            labels={"diff": "Разница", "name": ""},
            color="diff",
            color_continuous_scale="Reds",
        )
        fig3.update_yaxes(autorange="reversed")
        fig3.update_layout(title_x=0.5, showlegend=False)

        fig4 = px.bar(
            top_underrated,
            x="diff",
            y="name",
            orientation="h",
            title="Топ-10 недооценённых нами фильмов",
            labels={"diff": "Разница", "name": ""},
            color="diff",
            color_continuous_scale="Blues",
        )
        fig4.update_yaxes(autorange="reversed")
        fig4.update_layout(title_x=0.5, showlegend=False)

        # 5. Жанры — не таблица, а красивая treemap!
        genre_counts = self.genres
        fig5 = px.treemap(
            genre_counts,
            path=["name"],
            values="movies_count",
            title="Жанровая карта кинопоикы",
            color="movies_count",
            color_continuous_scale="Viridis",
        )
        fig5.update_layout(title_x=0.5)

        # Конвертируем в HTML div
        def to_div(fig):
            return plotly.offline.plot(fig, output_type="div", include_plotlyjs=False)

        graphs = {
            "kp_distribution": to_div(fig1),
            "club_vs_imdb": to_div(fig2),
            "overrated": to_div(fig3),
            "underrated": to_div(fig4),
            "genres_treemap": to_div(fig5),
        }

        return graphs

