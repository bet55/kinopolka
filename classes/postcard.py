import logging
from typing import Tuple, Dict, Optional
from postcard.models import Postcard
from postcard.serializers import PostcardSerializer
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import DatabaseError
from asgiref.sync import sync_to_async

# Configure logger
logger = logging.getLogger('kinopolka')


class PostcardHandler:
    """
    Класс для работы с открытками в базе данных
    """

    @classmethod
    async def create_postcard(cls, postcard_data: Dict) -> Tuple[Dict, bool]:
        """
        Создание новой открытки в базе. При этом предыдущие деактивируются.

        :param postcard_data: Словарь с информацией об открытке
        :return: кортеж (открытка, статус).
        """
        if not isinstance(postcard_data, dict):
            logger.error("Invalid postcard_data type: %s", type(postcard_data))
            return {"error": "Invalid data type"}, False

        try:
            # Deactivate previous postcards
            await cls.deactivate_postcard()

            # Wrap synchronous serializer operations
            serializer = PostcardSerializer(data=postcard_data)
            is_valid = await sync_to_async(serializer.is_valid)()

            if is_valid:
                postcard = await sync_to_async(serializer.save)()
                serializer = PostcardSerializer(postcard)  # Reserialize saved instance
                logger.info("Created postcard with data: %s", postcard_data)

                return await sync_to_async(lambda: serializer.data)(), True

            errors = await sync_to_async(lambda: serializer.errors)()
            logger.warning("Invalid postcard data: %s", errors)
            return errors, False

        except Exception as e:
            logger.error("Failed to create postcard: %s", str(e))
            return {"error": str(e)}, False

    @classmethod
    @sync_to_async
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
    async def get_postcard_by_id(cls, postcard_id: int) -> Optional[Dict]:
        """
        Получение открытки по Id.

        :param postcard_id: ID of the postcard to retrieve.

        :return: Информация об открытке.
        """
        if not isinstance(postcard_id, int) or postcard_id <= 0:
            logger.error("Invalid postcard_id: %s", postcard_id)
            return None

        try:
            postcard = await Postcard.objects.aget(id=postcard_id)
            serializer = PostcardSerializer(postcard)
            logger.info("Retrieved postcard with id: %s", postcard_id)
            return serializer.data

        except (ObjectDoesNotExist, MultipleObjectsReturned, DatabaseError) as e:
            logger.warning("Failed to retrieve postcard %s: %s", postcard_id, str(e))
            return None

    @classmethod
    @sync_to_async
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
    async def update_postcard(cls, data: Dict) -> Tuple[Optional[Dict], bool]:
        """
        Обновление информации об открытки.

        :param data: Dictionary containing postcard data with ID.

        :return: кортеж (открытка, статус обновления).
        """
        if not isinstance(data, dict) or "id" not in data:
            logger.error("Invalid update data: %s", data)
            return {"error": "Invalid data or missing ID"}, False

        try:
            postcard = await Postcard.objects.aget(id=data["id"])
            serializer = PostcardSerializer(postcard, data=data)

            if serializer.is_valid():
                await serializer.asave()
                logger.info("Updated postcard with id: %s", data["id"])
                return serializer.data, True

            logger.warning("Invalid update data for postcard %s: %s", data["id"], serializer.errors)
            return serializer.errors, False

        except (ObjectDoesNotExist, MultipleObjectsReturned, DatabaseError) as e:
            logger.warning("Failed to update postcard %s: %s", data.get("id"), str(e))
            return None, False

    @classmethod
    async def delete_postcard(cls, postcard_id: int) -> bool:
        """
        Удаление открытки по Id.

        :param postcard_id: ID of the postcard to delete.

        :return: True если всё успешно, иначе False.
        """
        if not isinstance(postcard_id, int) or postcard_id <= 0:
            logger.error("Invalid postcard_id for deletion: %s", postcard_id)
            return False

        try:
            postcard = await Postcard.objects.aget(id=postcard_id)
            await postcard.adelete()
            logger.info("Deleted postcard with id: %s", postcard_id)
            return True

        except (ObjectDoesNotExist, MultipleObjectsReturned, DatabaseError) as e:
            logger.warning("Failed to delete postcard %s: %s", postcard_id, str(e))
            return False

    @classmethod
    @sync_to_async
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
