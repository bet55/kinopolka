import logging

from adrf.views import APIView
from django.shortcuts import render
from rest_framework import status
from rest_framework.request import Request

from classes import MovieHandler, NoteHandler
from classes.movie import MoviesStructure
from mixins import GlobalDataMixin
from utils.response_handler import handle_response


# Configure logger
logger = logging.getLogger(__name__)


class MoviesViewSet(GlobalDataMixin, APIView):
    """
    Запросы на получение списков фильмов и их изменение.
    """

    http_method_names = ["get", "patch", "delete"]

    async def get(self, request: Request, kp_id: int | None = None):
        """
        Получение списка фильмов или фильма по ID.
        """

        if kp_id:
            movie = await MovieHandler.get_movie(kp_id)
            return handle_response(movie)

        response_format = request.query_params.get("format")
        is_archive = "archive" in request.path

        if response_format == "json":
            movies = await MovieHandler.get_all_movies(is_archive=is_archive)
            return handle_response(movies)

        movies = await MovieHandler.get_all_movies(info_type=MoviesStructure.posters, is_archive=is_archive)
        genres = MovieHandler.extract_genres(movies)
        context = {
            "movies": movies,
            "genres": genres,
            "is_archive": is_archive,
        }
        return render(
            request,
            "movies.html",
            context=await self.add_context_data(request, context),
        )

    async def patch(self, request: Request):
        """
        Изменение архивного статуса фильма.
        """
        kp_id = request.data.get("kp_id")
        is_archive = request.data.get("is_archive")

        result = await MovieHandler.change_movie_status(kp_id, is_archive)
        return handle_response(result, {"kp_id": kp_id, "is_archive": is_archive})

    async def delete(self, request: Request):
        """
        Удаление фильма.
        """
        kp_id = request.data.get("kp_id")

        result = await MovieHandler.remove_movie(kp_id)
        return handle_response(result, {"kp_id": kp_id}, status.HTTP_204_NO_CONTENT)


class MovieRatingViewSet(APIView):
    """
    Запросы на выставление и изменение рейтинга фильма.
    """

    http_method_names = ["post", "put", "delete"]

    async def delete(self, request: Request):
        """
        Удаление заметки с рейтингом фильма.
        """
        user_id = request.data.get("user_id")
        movie_kp_id = request.data.get("movie_kp_id")

        success = await NoteHandler.remove_note(user_id, movie_kp_id)
        return handle_response(
            success,
            {"user_id": user_id, "movie_kp_id": movie_kp_id},
            status.HTTP_204_NO_CONTENT,
        )

    async def post(self, request: Request):
        """
        Создание заметки с рейтингом.
        """
        note_data = request.data

        success = await NoteHandler.create_note(note_data)
        return handle_response(success, note_data, status.HTTP_201_CREATED)

    async def put(self, request: Request):
        """
        Изменение оценки или текста заметки с рейтингом.
        """
        note_data = request.data

        result = await NoteHandler.create_note(note_data)  # Handles updates via bulk_create
        return handle_response(result, note_data)


class MovieAddingViewSet(GlobalDataMixin, APIView):
    """
    Обработка добавления фильмов.
    """

    http_method_names = ["get", "post"]

    async def get(self, request: Request):
        """
        Форма для добавления фильма.
        """
        return render(request, "add_movie.html", context=await self.add_context_data(request, {}))

    async def post(self, request: Request):
        """
        Запрос на добавление фильма.
        """
        kp_id = "".join(char for char in str(request.data.get("kp_id", "-1")) if char.isdigit())

        result = await MovieHandler.a_download(kp_id)
        return handle_response(result, {"movie_id": result}, status.HTTP_201_CREATED)
