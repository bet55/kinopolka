from classes import NoteHandler, MovieHandler, MoviesStructure
from lists.models import Movie
import pandas as pd
import plotly
import plotly.express as px


class Statistic:
    """
    Класс для обработки статистики по просмотренным и ожидаемым фильмам из списков
    """

    @classmethod
    def get_movies_statistic(cls):

        film_model = Movie.mgr.filter(is_archive=True).values()
        df = pd.DataFrame(film_model)
        stats = {
            'total_duration': df['duration'].sum(),
            'rating_kp': round(df['rating_kp'].mean(), 2),
            'rating_imdb': round(df['rating_imdb'].mean(), 2),
            'count': len(df),
        }

        return stats

    @classmethod
    def most_popular_actor(cls):
        pass

    @classmethod
    def most_rated_kp_movies(cls):

        all_movies = MovieHandler.get_all_movies(MoviesStructure.rating.value, True)

        df = pd.DataFrame(all_movies)
        df['rating_kp'] = df['rating_kp'].astype(float)
        top_3 = df.groupby(['kp_id']).agg({'rating_kp': 'mean'}).reset_index().sort_values(by='rating_kp', ascending=False).head(3)

        top_3['poster'] = top_3.apply(lambda row: df[df.kp_id == row.kp_id]['poster'].values[0], axis=1)
        top_3['name'] = top_3.apply(lambda row: df[df.kp_id == row.kp_id]['name'].values[0], axis=1)
        top_rated_movies = top_3.to_dict('records')

        return top_rated_movies



    @classmethod
    def most_rated_users_movies(cls):
        movies = []
        notes = NoteHandler.get_all_notes('list')

        df = pd.DataFrame(notes)
        top_3 = df.groupby(['movie']).agg({'rating': 'mean'}).reset_index().sort_values(by='rating',ascending=False).head(3)

        for movie_id in list(top_3.movie):
            movies.append(MovieHandler.get_movie(movie_id))

        return movies

    @classmethod
    def draw(cls):
        film_model = Movie.mgr.filter(is_archive=True).values()
        df = pd.DataFrame(film_model)
        figure_config = {
            'x': 'rating_kp',
            'width': 800,
            'color_discrete_sequence': ['#9bab6e'],
            'labels': {'rating_kp': 'Средняя оценка пользователей', 'count': 'Количество оценок'},
        }
        figure = px.histogram(df, **figure_config)
        graph_div = plotly.offline.plot(figure, auto_open=False, output_type="div")

        return graph_div
