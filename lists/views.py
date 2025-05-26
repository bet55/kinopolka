import logging
from typing import Optional, Union
from django.shortcuts import render
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from adrf.views import APIView
from classes import MovieHandler, NoteHandler, Tools, UserHandler
from classes.movie import MoviesStructure
from mixins import GlobalDataMixin

# Configure logger
logger = logging.getLogger('kinopolka')


class MoviesView(GlobalDataMixin, APIView):
    """
    Запросы на получение списков фильмов и их изменение
    """

    async def get(self, request: Request, kp_id: Optional[int] = None) -> Response:
        """
        Получение списка фильмов или по id

        Args:
            request: HTTP request object.
            kp_id: Kinopoisk ID of a specific movie (optional).

        Returns:
            Response with movie data or rendered HTML page.
        """

        try:
            if kp_id:
                if not isinstance(kp_id, int) or kp_id <= 0:
                    logger.error("Invalid kp_id: %s", kp_id)
                    return Response(
                        {"success": False, "error": "Invalid kp_id", "data": None},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                movie = await MovieHandler.get_movie(kp_id)
                if not movie:
                    logger.warning("Movie not found: kp_id=%s", kp_id)
                    return Response(
                        {"success": False, "error": "Movie not found", "data": None},
                        status=status.HTTP_404_NOT_FOUND
                    )

                logger.info("Retrieved movie: kp_id=%s", kp_id)
                return Response(
                    {"success": True, "error": "", "data": movie},
                    status=status.HTTP_200_OK
                )

            response_format = request.query_params.get("format")
            is_archive = "archive" in request.path

            if response_format == "json":
                movies = await MovieHandler.get_all_movies(is_archive=is_archive)
                logger.info("Retrieved %d movies (is_archive=%s)", len(movies), is_archive)
                return Response(
                    {"success": True, "error": "", "data": movies},
                    status=status.HTTP_200_OK
                )

            movies = await MovieHandler.get_all_movies(info_type=MoviesStructure.posters.value, is_archive=is_archive)
            genres = MovieHandler.extract_genres(movies)

            context = {
                "movies": movies,
                "genres": genres,
                "is_archive": is_archive,
            }
            logger.info("Rendering movies.html with %d movies (is_archive=%s)", len(movies), is_archive)
            return render(request, "movies.html", context=await self.add_context_data(request, context))

        except Exception as e:
            logger.error("Failed to process GET request: %s", str(e))
            return Response(
                {"success": False, "error": str(e), "data": None},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    async def patch(self, request: Request) -> Response:
        """
        Изменение архивного статуса

        Args:
            request: HTTP request object containing kp_id and is_archive.

        Returns:
            Response indicating success or failure.
        """
        try:
            kp_id = int(request.data.get("kp_id", -1))
            is_archive = request.data.get("is_archive")

            if kp_id <= 0:
                logger.error("Invalid kp_id: %s", kp_id)
                return Response(
                    {"success": False, "error": "Invalid or missing kp_id", "data": None},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not isinstance(is_archive, bool):
                logger.error("Invalid is_archive: %s", is_archive)
                return Response(
                    {"success": False, "error": "Invalid is_archive value", "data": None},
                    status=status.HTTP_400_BAD_REQUEST
                )

            success = await MovieHandler.change_movie_status(kp_id, is_archive)
            if not success:
                logger.warning("Failed to update movie status: kp_id=%s", kp_id)
                return Response(
                    {"success": False, "error": "Фильм не найден или проблема обновления", "data": None},
                    status=status.HTTP_404_NOT_FOUND
                )

            logger.info("Updated movie status: kp_id=%s, is_archive=%s", kp_id, is_archive)
            return Response(
                {"success": True, "error": "", "data": {"kp_id": kp_id, "is_archive": is_archive}},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error("Failed to process PATCH request: %s", str(e))
            return Response(
                {"success": False, "error": str(e), "data": None},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    async def delete(self, request: Request) -> Response:
        """
        Удаление фильма

        Args:
            request: HTTP request object containing kp_id.

        Returns:
            Response indicating success or failure.
        """
        try:
            kp_id = int(request.data.get("kp_id", -1))

            if kp_id <= 0:
                logger.error("Invalid or missing kp_id: %s", kp_id)
                return Response(
                    {"success": False, "error": "Invalid or missing kp_id", "data": None},
                    status=status.HTTP_400_BAD_REQUEST
                )

            success = await MovieHandler.remove_movie(kp_id)
            if not success:
                logger.warning("Failed to delete movie: kp_id=%s", kp_id)
                return Response(
                    {"success": False, "error": "Movie not found or deletion failed", "data": None},
                    status=status.HTTP_404_NOT_FOUND
                )

            logger.info("Deleted movie: kp_id=%s", kp_id)
            return Response(
                {"success": True, "error": "", "data": {"kp_id": kp_id}},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error("Failed to process DELETE request: %s", str(e))
            return Response(
                {"success": False, "error": str(e), "data": None},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MovieRatingView(APIView):
    """
    Запросы на выставление и изменение рейтинга фильма
    """

    async def delete(self, request: Request) -> Response:
        """
        Удаление заметки с рейтингом фильма

        Args:
            request: HTTP request object containing user_id and movie_kp_id.

        Returns:
            Response indicating success or failure.
        """
        try:
            user_id = int(request.data.get("user_id", -1))
            movie_kp_id = int(request.data.get("movie_kp_id", -1))

            if user_id <= 0:
                logger.error("Invalid or missing user_id: %s", user_id)
                return Response(
                    {"success": False, "error": "Invalid or missing user_id", "data": None},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if movie_kp_id <= 0:
                logger.error("Invalid or missing movie_kp_id: %s", movie_kp_id)
                return Response(
                    {"success": False, "error": "Invalid or missing movie_kp_id", "data": None},
                    status=status.HTTP_400_BAD_REQUEST
                )

            success = await NoteHandler.remove_note(user_id, movie_kp_id)
            if not success:
                logger.warning("Failed to delete note: user_id=%s, movie_kp_id=%s", user_id, movie_kp_id)
                return Response(
                    {"success": False, "error": "Note not found or deletion failed", "data": None},
                    status=status.HTTP_404_NOT_FOUND
                )

            logger.info("Deleted note: user_id=%s, movie_kp_id=%s", user_id, movie_kp_id)
            return Response(
                {"success": True, "error": "", "data": {"user_id": user_id, "movie_kp_id": movie_kp_id}},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error("Failed to process DELETE request: %s", str(e))
            return Response(
                {"success": False, "error": str(e), "data": None},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    async def post(self, request: Request) -> Response:
        """
        Создание заметки с рейтингом

        Args:
            request: HTTP request object containing note data (user, movie, rating, optional text).

        Returns:
            Response indicating success or failure.
        """
        try:
            note_data = request.data
            if not isinstance(note_data, dict) or not all(key in note_data for key in ["user", "movie", "rating"]):
                logger.error("Invalid note data: %s", note_data)
                return Response(
                    {"success": False, "error": "Invalid or missing note data", "data": None},
                    status=status.HTTP_400_BAD_REQUEST
                )

            success = await NoteHandler.create_note(note_data)
            if not success:
                logger.warning("Failed to create note: %s", note_data)
                return Response(
                    {"success": False, "error": "Failed to create note", "data": None},
                    status=status.HTTP_400_BAD_REQUEST
                )

            logger.info("Created note: user=%s, movie=%s", note_data.get("user"), note_data.get("movie"))
            return Response(
                {"success": True, "error": "", "data": note_data},
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            logger.error("Failed to process POST request: %s", str(e))
            return Response(
                {"success": False, "error": str(e), "data": None},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    async def put(self, request: Request) -> Response:
        """
        Изменение оценки или текста заметки с рейтингом

        Args:
            request: HTTP request object containing updated note data (user, movie, rating, optional text).

        Returns:
            Response indicating success or failure.
        """
        try:
            note_data = request.data
            if not isinstance(note_data, dict) or not all(key in note_data for key in ["user", "movie", "rating"]):
                logger.error("Invalid note data: %s", note_data)
                return Response(
                    {"success": False, "error": "Invalid or missing note data", "data": None},
                    status=status.HTTP_400_BAD_REQUEST
                )

            success = await NoteHandler.create_note(note_data)  # create_note handles updates via bulk_create
            if not success:
                logger.warning("Failed to update note: %s", note_data)
                return Response(
                    {"success": False, "error": "Failed to update note", "data": None},
                    status=status.HTTP_400_BAD_REQUEST
                )

            logger.info("Updated note: user=%s, movie=%s", note_data.get("user"), note_data.get("movie"))
            return Response(
                {"success": True, "error": "", "data": note_data},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error("Failed to process PUT request: %s", str(e))
            return Response(
                {"success": False, "error": str(e), "data": None},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MovieAdditionView(GlobalDataMixin, APIView):
    """
    Обработка добавления фильмов
    """

    async def get(self, request: Request) -> Response:
        """
        Форма для добавления

        Args:
            request: HTTP request object.

        Returns:
            Rendered HTML page for adding a movie.
        """
        try:
            logger.info("Rendering add_movie.html")
            return render(request, "add_movie.html", context=await self.add_context_data(request, {}))

        except Exception as e:
            logger.error("Failed to render add_movie.html: %s", str(e))
            return Response(
                {"success": False, "error": str(e), "data": None},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    async def post(self, request: Request) -> Response:
        """
        Запрос на добавление

        Args:
            request: HTTP request object containing kp_id.

        Returns:
            Response indicating success or failure of movie addition.
        """
        try:
            kp_id = request.data.get("kp_id", "-1")
            # Sanitize kp_id to digits only
            kp_id = "".join(char for char in str(kp_id) if char.isdigit())

            if int(kp_id) <= 0:
                logger.error("Invalid or missing kp_id: %s", kp_id)
                return Response(
                    {"success": False, "error": "Invalid or missing kp_id", "data": None},
                    status=status.HTTP_400_BAD_REQUEST
                )

            movie_id, success = await MovieHandler.a_download(kp_id)
            if not success:
                logger.warning("Failed to download movie: kp_id=%s", kp_id)
                return Response(
                    {"success": False, "error": "Failed to download movie", "data": None},
                    status=status.HTTP_400_BAD_REQUEST
                )

            logger.info("Downloaded movie: kp_id=%s, movie_id=%s", kp_id, movie_id)
            return Response(
                {"success": True, "error": "", "data": {"movie_id": movie_id}},
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            logger.error("Failed to process POST request: %s", str(e))
            return Response(
                {"success": False, "error": str(e), "data": None},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
