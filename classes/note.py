from collections import defaultdict
import logging

from asgiref.sync import sync_to_async
from rest_framework.exceptions import ValidationError

from lists.models import Movie, Note, User
from lists.serializers import NoteSerializer
from pydantic_models import RateMovieRequestModel
from utils.exception_handler import handle_exceptions


# Configure logger
logger = logging.getLogger(__name__)


class NoteHandler:
    """
    Класс для работы с записями оценок в базе данных.
    """

    @classmethod
    @handle_exceptions("Заметки")
    @sync_to_async
    def get_all_notes(cls, result_format: str = "dict", movie_info: bool = False) -> dict[int, list[dict]] | list[dict]:
        """
        Получение всех заметок с оценками фильмов.
        :param result_format: Формат возвращаемых данных ('dict' для группировки по movie_id, иначе 'list').
        :param movie_info: нужно ли добывать по внешним ключам информацию о фильмах.
        :return: Словарь {movie_id: [заметки]} или список заметок.
        """
        if result_format not in ("dict", "list"):
            raise ValidationError("Некорректный result_format")

        raw_notes = Note.mgr.all()
        serialized_notes = NoteSerializer(raw_notes, many=True).data
        logger.info("Получено %d заметок", raw_notes.count())

        if result_format == "list":
            return serialized_notes

        notes = defaultdict(list)
        for note in serialized_notes:
            notes[note["movie"]].append(note)

        return dict(notes)

    @classmethod
    @handle_exceptions("Заметка")
    async def create_note(cls, note_body: dict) -> int:
        """
        Создание или обновление заметки с оценкой о фильме.
        :param note_body: Данные заметки (user ID, movie kp_id, rating, optional text).
        :return: True если успешно.
        """
        if not isinstance(note_body, dict):
            raise ValidationError("Некорректный тип данных note_body")

        if not isinstance(note_body, dict) or not all(key in note_body for key in ["user", "movie", "rating"]):
            raise ValidationError("Некорректные данные заметки")

        try:
            modeling = RateMovieRequestModel(**note_body)
            formatted_request = modeling.model_dump(exclude_none=True, exclude_defaults=True, exclude_unset=True)
        except RateMovieRequestModel.ValidationError as e:
            logger.warning("Некорректные данные заметки: %s", str(e))
            raise ValidationError("Некорректные данные заметки")

        if not all(key in formatted_request for key in ["user", "movie", "rating"]):
            raise ValidationError("Отсутствуют обязательные поля в note_body")

        user = await User.objects.aget(id=formatted_request["user"])
        film = await Movie.mgr.aget(kp_id=formatted_request["movie"])
        rating = formatted_request["rating"]

        note = Note(user=user, movie=film, rating=rating)
        if "text" in formatted_request:
            note.text = formatted_request["text"]

        await Note.mgr.abulk_create(
            [note],
            update_conflicts=True,
            update_fields=["rating", "text"],
            unique_fields=["movie", "user"],
        )
        logger.info(
            "Создана/обновлена заметка для пользователя %s, фильма %s",
            user.id,
            film.kp_id,
        )
        note_id = note.id
        return note_id

    @classmethod
    @handle_exceptions("Заметка")
    async def remove_note(cls, user_id: int, movie_kp_id: int) -> int:
        """
        Удаление заметки для конкретного пользователя и фильма.
        :param user_id: ID пользователя, создавшего заметку.
        :param movie_kp_id: Kinopoisk ID фильма.
        :return: True если успешно.
        """
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValidationError("Некорректный user_id")
        if not isinstance(movie_kp_id, int) or movie_kp_id <= 0:
            raise ValidationError("Некорректный movie_kp_id")

        note = await Note.mgr.aget(user__id=user_id, movie__kp_id=movie_kp_id)
        note_id = note.id
        await note.adelete()
        logger.info("Удалена заметка для пользователя %s, фильма %s", user_id, movie_kp_id)
        return note_id
