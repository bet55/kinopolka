from classes.exceptions import TooManyActivePostcardsError
from postcard.models import Postcard
from postcard.serializers import PostcardSerializer


class PostcardHandler:
    '''
    Класс для работы с открытками в базе данных
    '''
    @classmethod
    def create_postcard(cls, postcard_data: dict) -> (dict, bool):
        serializer = PostcardSerializer(data=postcard_data)
        if serializer.is_valid():

            #при создании новой карточки все существующие становятся неактивными
            active_postcards = Postcard.objects.filter(is_active=True)
            for active_postcard in active_postcards:
                cls._deactivate_postcard(active_postcard)

            serializer.save()
            return serializer.data, True
        return serializer.errors, False

    @classmethod
    def get_postcard(cls, postcard_id: int) -> dict | None:
        try:
            postcard = Postcard.objects.get(id=postcard_id)
            serializer = PostcardSerializer(postcard)
        except Postcard.DoesNotExist:
            return None
        return serializer.data

    @classmethod
    def get_all_postcards(cls) -> dict:
        postcards = Postcard.objects.all()
        serializer = PostcardSerializer(postcards, many=True)
        return serializer.data

    @classmethod
    def update_postcard(cls, data: dict) -> (dict | None, bool):
        try:
            postcard = Postcard.objects.get(id=data['id'])
        except Postcard.DoesNotExist:
            return None, False
        serializer = PostcardSerializer(postcard, data=data)
        if serializer.is_valid():
            serializer.save()
            return serializer.data, True
        return serializer.errors, False

    @classmethod
    def delete_postcard(cls, postcard_id: int) -> None | tuple:
        try:
            postcard = Postcard.objects.get(id=postcard_id)
        except Postcard.DoesNotExist:
            return None
        return postcard.delete()

    @staticmethod
    def _deactivate_postcard(postcard) -> bool:
        postcard.is_active = False
        try:
            postcard.save()
        except Postcard.DoesNotExist:
            return False
        return True

    @staticmethod
    def get_active_postcard() -> Postcard:
        active_postcards = Postcard.objects.filter(is_active=True)
        if len(active_postcards) != 1:
            raise TooManyActivePostcardsError
        return active_postcards[0]
