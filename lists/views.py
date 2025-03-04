from django.shortcuts import render
from rest_framework.renderers import HTMLFormRenderer
from rest_framework.request import Request
from rest_framework.response import Response

from rest_framework.views import APIView

from classes import MovieHandler, NoteHandler, Tools, UserHandler


class MoviesView(APIView):
    """
    Запросы на получение списков фильмов и их изменение
    """

    def get(self, request: Request, kp_id: int = None):
        """
        Получение списка фильмов или по id
        """
        if kp_id:
            return Response(MovieHandler.get_movie(kp_id=kp_id))

        response_format = request.query_params.get('format')
        is_archive = 'archive' in request.path

        if response_format == 'json':
            return Response(MovieHandler.get_all_movies(is_archive=is_archive))

        return render(
            request,
            'movies.html',
            context={
                'movies': MovieHandler.get_all_movies(all_info=False, is_archive=is_archive),
                'users': UserHandler.get_all_users(),
                'is_archive': is_archive,
                'random': Tools.get_random_images(),
            }
        )

    def patch(self, request: Request):
        """
        Изменение архивного статуса
        """
        kp_id = request.data['kp_id']
        is_archive = request.data['is_archive']

        success = MovieHandler.change_movie_status(kp_id, is_archive)

        return Response(
            data={
                'success': str(success),
                'error': '',
                'id': kp_id,
            }
        )

    def delete(self, request: Request):
        """
        Удаление фильма
        """
        kp_id = request.data.get('kp_id')

        if not kp_id:
            return Response(
                data={
                    'success': False,
                    'error': 'Lost kp_id',
                    'id': False,
                }
            )

        movie_is_deleted = MovieHandler.remove_movie(kp_id)

        return Response(
            data={
                'success': str(movie_is_deleted),
                'error': '',
                'id': kp_id,
            }
        )


class MovieRatingView(APIView):
    """
    Запросы на выставление и изменение рейтинга фильма
    """

    def delete(self, request: Request):
        """
        Удаление заметки с рейтингом фильма
        """
        success = NoteHandler.remove_note(request.data['user'], request.data['film'])

        return Response(
            data={
                'success': bool(success),
                'error': str(success),
            }
        )

    def post(self, request: Request):
        """
        Создание заметки с рейтингом
        """
        success = NoteHandler.create_note(request.data)

        return Response(
            data={
                'success': success,
                'error': '',
            }
        )

    def put(self, request: Request):
        """
        Изменение оценки или текста рейтингом
        """
        self.post(request)


class MovieAdditionView(APIView):
    """
    Обработка добавления фильмов
    """

    def get(self, request: Request):
        """
        Форма для добавления
        """
        return render(
            request,
            'add_movie.html',
            context={
                'random': Tools.get_random_images(),
                'users': UserHandler.get_all_users(),
            }
        )

    def post(self, request: Request):
        """
        Запрос на добавление
        """
        kp_id = ''.join(char for char in list(request.data.get('kp_id', '')) if char.isdigit())

        movie_id, success = MovieHandler.download(kp_id)

        return Response(
            data={
                'success': success,
                'error': '',
                'id': movie_id,
            }
        )
