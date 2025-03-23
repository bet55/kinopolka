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

    @classmethod
    def deactivate_postcard(cls, postcard_id: int) -> bool:
        try:
            postcard = Postcard.objects.get(id=postcard_id)
        except Postcard.DoesNotExist:
            return False
        postcard.is_active = False
        postcard.save()
        return True
