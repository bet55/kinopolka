from postcard.models import Postcard
from postcard.serializers import PostcardSerializer
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import DatabaseError


class PostcardHandler:
    """
    Класс для работы с открытками в базе данных
    """

    @classmethod
    def create_postcard(cls, postcard_data: dict) -> (dict, bool):
        cls.deactivate_postcard()

        serializer = PostcardSerializer(data=postcard_data)
        # todo raise valid error
        if serializer.is_valid():
            serializer.save()
            return serializer.data, True
        return serializer.errors, False

    @classmethod
    def get_postcard(cls) -> (Postcard | None, bool):
        """
        Возвращаем последнюю активную открытку и статус открытки
        """
        try:
            postcard = Postcard.objects.filter(is_active=True).latest("created_at")
            postcard = get_object_or_404(Postcard, pk=postcard.id)
            return postcard

        except (ObjectDoesNotExist, MultipleObjectsReturned, DatabaseError):
            return None

    @classmethod
    def get_postcard_by_id(cls, postcard_id: int) -> dict | None:
        try:
            postcard = Postcard.objects.get(id=postcard_id)
            serializer = PostcardSerializer(postcard)
            return serializer.data

        except (ObjectDoesNotExist, MultipleObjectsReturned, DatabaseError):
            return None

    @classmethod
    def get_all_postcards(cls) -> dict:
        postcards = Postcard.objects.all()
        serializer = PostcardSerializer(postcards, many=True)
        return serializer.data

    @classmethod
    def update_postcard(cls, data: dict) -> (dict | None, bool):
        try:
            postcard = Postcard.objects.get(id=data["id"])
        except (ObjectDoesNotExist, MultipleObjectsReturned, DatabaseError):
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
        except (ObjectDoesNotExist, MultipleObjectsReturned, DatabaseError):
            return None
        return postcard.delete()

    @classmethod
    def deactivate_postcard(cls, postcard_id: int = None, update_all=True) -> bool:
        try:
            if update_all:
                Postcard.objects.all().update(is_active=False)
                return True

            postcard = Postcard.objects.get(id=postcard_id)
            postcard.is_active = False
            postcard.save()
            return True

        except (ObjectDoesNotExist, MultipleObjectsReturned, DatabaseError):
            return False
