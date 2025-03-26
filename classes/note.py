from lists.models import Note, User, Movie
from lists.serializers import NoteSerializer
from collections import defaultdict

from pydantic_models import RateMovieRequestModel


class NoteHandler:
    """
    Класс для работы с записями оценок в базе данных
    """
    @classmethod
    def get_all_notes(cls, result_format = 'dict') -> dict[int, list]:
        notes = defaultdict(list)

        raw_notes = Note.mgr.all()
        serialize = NoteSerializer(raw_notes, many=True).data

        if result_format == 'list':
            return serialize

        for note in serialize:
            notes[note['movie']].append(note)

        return dict(notes)

    @classmethod
    def create_note(cls, note_body: dict):
        modeling = RateMovieRequestModel(**note_body)
        formated_request = modeling.model_dump(exclude_none=True, exclude_defaults=True, exclude_unset=True)

        # formated_request['user'] = AppUser.objects.get(id=formated_request['user'])
        # formated_request['film'] = Film.mgr.get(kp_id=formated_request['film'])

        user = User.objects.get(id=formated_request['user'])
        film = Movie.mgr.get(kp_id=formated_request['film'])
        rating = formated_request['rating']

        # Todo Хак, нужно переписать на create_or_update
        sticky_model = [Note(user=user, film=film, rating=rating)]

        res = Note.mgr.bulk_create(sticky_model,
                                          update_conflicts=True,
                                          update_fields=['rating', 'text'],
                                          unique_fields=['film', 'user'])
        return True

    @classmethod
    def remove_note(cls, user, film):
        note = Note.mgr.get(user=user, film=film)
        return note.delete()
