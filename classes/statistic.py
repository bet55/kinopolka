import logging

import numpy as np
import pandas as pd
import plotly
import plotly.express as px
from icecream import ic

from classes import MovieHandler, MoviesStructure, NoteHandler

logger = logging.getLogger(__name__)


class Statistic:
    """
    Класс для обработки статистики по просмотренным и ожидаемым фильмам из списков
    """

    TOP_MOVIES = 4

    @classmethod
    async def get_movies_statistic(cls):

        film_model = await MovieHandler.get_all_movies(is_archive=True)
        df = pd.DataFrame(film_model.values())

        # почему-то слетают типы нужно проверить сериалайзер
        df.loc[:, ["duration", "rating_kp", "rating_imdb"]] = df.loc[
            :, ["duration", "rating_kp", "rating_imdb"]
        ].astype(np.float16)

        notes = await NoteHandler.get_all_notes("list")
        notes = pd.DataFrame(notes)
        users_mean_rating = (
            notes.groupby(["movie"]).agg({"rating": "mean"}).rating.mean().round(2)
        )

        stats = {
            "total_duration": df["duration"].sum(),
            "rating_kp": df["rating_kp"].mean().round(2),
            "rating_imdb": df["rating_imdb"].mean().round(2),
            "rating_kinopolka": users_mean_rating,
            "count": len(df),
        }

        return stats

    @classmethod
    def most_popular_actor(cls):
        pass

    @classmethod
    async def most_rated_imdb_movies(cls):

        all_movies = await MovieHandler.get_all_movies(
            MoviesStructure.rating.value, True
        )

        df = pd.DataFrame(all_movies)
        df["rating_imdb"] = df["rating_imdb"].astype(float)
        top_movies = (
            df.groupby(["kp_id"])
            .agg({"rating_imdb": "mean"})
            .reset_index()
            .sort_values(by="rating_imdb", ascending=False)
            .head(cls.TOP_MOVIES)
        )

        top_movies["poster_local"] = top_movies.apply(
            lambda row: df[df.kp_id == row.kp_id]["poster_local"].values[0], axis=1
        )
        top_movies["name"] = top_movies.apply(
            lambda row: df[df.kp_id == row.kp_id]["name"].values[0], axis=1
        )
        top_rated_movies = top_movies.to_dict("records")

        return top_rated_movies

    @classmethod
    async def most_rated_users_movies(cls):
        movies = []
        notes = await NoteHandler.get_all_notes("list")

        df = pd.DataFrame(notes)

        top_movies = (
            df.groupby(["movie"])
            .agg({"rating": "mean"})
            .reset_index()
            .sort_values(by="rating", ascending=False)
            .head(cls.TOP_MOVIES)
        )

        for movie_id in list(top_movies.movie):
            movies.append(await MovieHandler.get_movie(movie_id))

        return movies

    @classmethod
    async def draw(cls):
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
