import logging
from typing import Tuple, Dict, Optional
from postcard.models import Postcard
from postcard.serializers import PostcardSerializer
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import DatabaseError

# Configure logger
logger = logging.getLogger('kinopolka')


class PostcardHandler:
    """
    Класс для работы с открытками в базе данных
    """

    @classmethod
    def create_postcard(cls, postcard_data: Dict) -> Tuple[Dict, bool]:
        """
        Создание новой открытки в базе. При этом предыдущие деактивируются.

        :param postcard_data: Словарь с информацией об открытке
        :return: кортеж (открытка, статус).
        """
        if not isinstance(postcard_data, dict):
            logger.error("Invalid postcard_data type: %s", type(postcard_data))
            return {"error": "Invalid data type"}, False

        try:
            # Перед созданием новой открытки деактивируем прошлую
            cls.deactivate_postcard()
            serializer = PostcardSerializer(data=postcard_data)

            if serializer.is_valid():
                serializer.save()
                logger.info("Created postcard with data: %s", postcard_data)
                return serializer.data, True

            logger.warning("Invalid postcard data: %s", serializer.errors)
            return serializer.errors, False

        except Exception as e:
            logger.error("Failed to create postcard: %s", str(e))
            return {"error": str(e)}, False

    @classmethod
    def get_postcard(cls) -> Tuple[Optional[Postcard], bool]:
        """
        Получение активной открытки. Активная открытка - эта та, которая будет отображаться у пользователей на сайте

        :return: Информация об открытке.
        """
        try:
            postcard = Postcard.objects.filter(is_active=True).latest("created_at")
            postcard = get_object_or_404(Postcard, pk=postcard.id)
            logger.info("Retrieved active postcard with id: %s", postcard.id)
            return postcard, True

        except (ObjectDoesNotExist, MultipleObjectsReturned, DatabaseError) as e:
            logger.warning("Failed to retrieve active postcard: %s", str(e))
            return None, False

    @classmethod
    def get_postcard_by_id(cls, postcard_id: int) -> Optional[Dict]:
        """
        Получение открытки по Id.

        :param postcard_id: ID of the postcard to retrieve.

        :return: Информация об открытке.
        """
        if not isinstance(postcard_id, int) or postcard_id <= 0:
            logger.error("Invalid postcard_id: %s", postcard_id)
            return None

        try:
            postcard = Postcard.objects.get(id=postcard_id)
            serializer = PostcardSerializer(postcard)
            logger.info("Retrieved postcard with id: %s", postcard_id)
            return serializer.data

        except (ObjectDoesNotExist, MultipleObjectsReturned, DatabaseError) as e:
            logger.warning("Failed to retrieve postcard %s: %s", postcard_id, str(e))
            return None

    @classmethod
    def get_all_postcards(cls) -> Dict:
        """
        Получение всех открыток.

        :return: Информация обо всех открытках.
        """
        try:
            postcards = Postcard.objects.all()
            serializer = PostcardSerializer(postcards, many=True)
            logger.info("Retrieved %s postcards", postcards.count())
            return serializer.data

        except Exception as e:
            logger.error("Failed to retrieve postcards: %s", str(e))
            return {}

    @classmethod
    def update_postcard(cls, data: Dict) -> Tuple[Optional[Dict], bool]:
        """
        Обновление информации об открытки.

        :param data: Dictionary containing postcard data with ID.

        :return: кортеж (открытка, статус обновления).
        """
        if not isinstance(data, dict) or "id" not in data:
            logger.error("Invalid update data: %s", data)
            return {"error": "Invalid data or missing ID"}, False

        try:
            postcard = Postcard.objects.get(id=data["id"])
            serializer = PostcardSerializer(postcard, data=data)

            if serializer.is_valid():
                serializer.save()
                logger.info("Updated postcard with id: %s", data["id"])
                return serializer.data, True

            logger.warning("Invalid update data for postcard %s: %s", data["id"], serializer.errors)
            return serializer.errors, False

        except (ObjectDoesNotExist, MultipleObjectsReturned, DatabaseError) as e:
            logger.warning("Failed to update postcard %s: %s", data.get("id"), str(e))
            return None, False

    @classmethod
    def delete_postcard(cls, postcard_id: int) -> bool:
        """
        Удаление открытки по Id.

        :param postcard_id: ID of the postcard to delete.

        :return: True если всё успешно, иначе False.
        """
        if not isinstance(postcard_id, int) or postcard_id <= 0:
            logger.error("Invalid postcard_id for deletion: %s", postcard_id)
            return False

        try:
            postcard = Postcard.objects.get(id=postcard_id)
            postcard.delete()
            logger.info("Deleted postcard with id: %s", postcard_id)
            return True

        except (ObjectDoesNotExist, MultipleObjectsReturned, DatabaseError) as e:
            logger.warning("Failed to delete postcard %s: %s", postcard_id, str(e))
            return False

    @classmethod
    def deactivate_postcard(cls, postcard_id: Optional[int] = None, update_all: bool = True) -> bool:
        """
        Деактивация одной или всех открыток.

        :param postcard_id: Id открытки для деактивации.
        :param update_all: Деактивируем все открытки.

        :return: True если всё успешно, иначе False.
        """
        try:
            if update_all:
                count = Postcard.objects.all().update(is_active=False)
                logger.info("Deactivated %s postcards", count)
                return True

            if not isinstance(postcard_id, int) or postcard_id <= 0:
                logger.error("Invalid postcard_id for deactivation: %s", postcard_id)
                return False

            postcard = Postcard.objects.get(id=postcard_id)
            postcard.is_active = False
            postcard.save()
            logger.info("Deactivated postcard with id: %s", postcard_id)
            return True

        except (ObjectDoesNotExist, MultipleObjectsReturned, DatabaseError) as e:
            logger.warning("Failed to deactivate postcard(s): %s", str(e))
            return False