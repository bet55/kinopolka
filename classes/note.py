import logging
from typing import Dict, List, Union
from collections import defaultdict
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import IntegrityError
from lists.models import Note, User, Movie
from lists.serializers import NoteSerializer
from pydantic_models import RateMovieRequestModel
from asgiref.sync import sync_to_async


# Configure logger
logger = logging.getLogger('kinopolka')


class NoteHandler:
    """
    Класс для работы с записями оценок в базе данных
    """

    @classmethod
    @sync_to_async
    def get_all_notes(cls, result_format: str = "dict") -> Union[Dict[int, List[Dict]], List[Dict]]:
        """
        Получение всех заметок с оценками фильмов.

        :param result_format: Формат заметок. "Dict" для группировки заметок по id фильма - возвращает словарь.
         Иначе возвращается list с плоской структурой.

        :return:
            Если result_format = "dict", возвращает словарь {movie Id: [заметки фильма]}.
            Если result_format != "dict", возвращает список [список заметок].
            При ошибке возвращает пустой словарь или массив.
        """
        if result_format not in ("dict", "list"):
            logger.error("Invalid result_format: %s", result_format)
            return {} if result_format == "dict" else []

        try:
            raw_notes = Note.mgr.all()
            serialized_notes = NoteSerializer(raw_notes, many=True).data
            logger.info("Retrieved %d notes", raw_notes.count())

            if result_format == "list":
                return serialized_notes

            notes = defaultdict(list)
            for note in serialized_notes:
                notes[note["movie"]].append(note)

            return dict(notes)

        except Exception as e:
            logger.error("Failed to retrieve notes: %s", str(e))
            return {} if result_format == "dict" else []

    @classmethod
    async def create_note(cls, note_body: Dict) -> bool:
        """
        Создаём или обновляем заметку с оценкой о фильме.

        :param note_body: Информация о заметке (user ID, movie kp_id, rating, optional text).

        :return: True если всё успешно, иначе False.
        """
        if not isinstance(note_body, dict):
            logger.error("Invalid note_body type: %s", type(note_body))
            return False

        try:
            # Validate Pydantic model
            modeling = RateMovieRequestModel(**note_body)
            formatted_request = modeling.model_dump(
                exclude_none=True, exclude_defaults=True, exclude_unset=True
            )

            # Validate required fields
            if not all(key in formatted_request for key in ["user", "movie", "rating"]):
                logger.error("Missing required fields in note_body: %s", formatted_request)
                return False

            # Fetch user and movie
            user = User.objects.aget(id=formatted_request["user"])
            film = Movie.mgr.aget(kp_id=formatted_request["movie"])
            rating = formatted_request["rating"]

            # Create note object
            note = Note(user=user, movie=film, rating=rating)
            if "text" in formatted_request:
                note.text = formatted_request["text"]

            # Use bulk_create for upsert (create or update)
            Note.mgr.abulk_create(
                [note],
                update_conflicts=True,
                update_fields=["rating", "text"],
                unique_fields=["movie", "user"],
            )
            logger.info("Created/updated note for user %s, movie %s", user.id, film.kp_id)
            return True

        except RateMovieRequestModel.ValidationError as e:
            logger.warning("Invalid note data: %s", str(e))
            return False
        except (ObjectDoesNotExist, MultipleObjectsReturned, IntegrityError) as e:
            logger.warning("Failed to create note: %s", str(e))
            return False
        except Exception as e:
            logger.error("Unexpected error creating note: %s", str(e))
            return False

    @classmethod
    async def remove_note(cls, user_id: int, movie_kp_id: int) -> bool:
        """
        Remove a movie note for a specific user and movie.

        :param user_id: ID of the user who created the note.
        :param movie_kp_id: Kinopoisk ID of the movie.

        :return: True если всё успешно, иначе False.
        """
        if not isinstance(user_id, int) or user_id <= 0:
            logger.error("Invalid user_id: %s", user_id)
            return False

        if not isinstance(movie_kp_id, int) or movie_kp_id <= 0:
            logger.error("Invalid movie_kp_id: %s", movie_kp_id)
            return False

        try:
            note = Note.mgr.aget(user__id=user_id, movie__kp_id=movie_kp_id)
            note.adelete()
            logger.info("Deleted note for user %s, movie %s", user_id, movie_kp_id)
            return True

        except (ObjectDoesNotExist, MultipleObjectsReturned) as e:
            logger.warning("Failed to delete note for user %s, movie %s: %s", user_id, movie_kp_id, str(e))
            return False
        except Exception as e:
            logger.error("Unexpected error deleting note for user %s, movie %s: %s", user_id, movie_kp_id, str(e))
            return False
