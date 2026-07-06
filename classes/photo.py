import logging
import os

from asgiref.sync import sync_to_async
from rest_framework.exceptions import ValidationError

from features.models import Photo
from features.serializers import PhotoSerializer
from utils.exception_handler import handle_exceptions


logger = logging.getLogger(__name__)


class PhotoHandler:
    @staticmethod
    @handle_exceptions("Фотографии")
    @sync_to_async
    def get_all_photos() -> list[dict]:
        """
        Получение всех фотографий клуба (свежие сверху)
        :return: список сериализованных фотографий
        """
        photos = Photo.objects.all()
        return PhotoSerializer(photos, many=True).data

    @staticmethod
    @handle_exceptions("Фотография")
    @sync_to_async
    def create_photo(data: dict) -> dict:
        """
        Загрузка новой фотографии
        :param data: словарь с данными (image — файл, name, description)
        :return: сериализованные данные фотографии
        """
        image = data.get("image")
        if not image:
            raise ValidationError("Нужен файл изображения")

        # Без названия — берём имя файла без расширения
        name = (data.get("name") or "").strip() or os.path.splitext(image.name)[0]
        photo = Photo.objects.create(
            name=name,
            description=data.get("description", ""),
            image=image,
        )
        return PhotoSerializer(photo).data

    @staticmethod
    @handle_exceptions("Фотография")
    async def update_photo(photo_id: int, data: dict) -> dict:
        """
        Обновление названия/описания фотографии (сам файл не меняем)
        :param photo_id: ID фотографии
        :param data: словарь с обновляемыми полями (name, description)
        :return: сериализованные данные фотографии
        """
        photo = await Photo.objects.aget(pk=photo_id)

        if (data.get("name") or "").strip():
            photo.name = data["name"].strip()
        if "description" in data:
            photo.description = data["description"]

        await photo.asave()
        return await sync_to_async(lambda: PhotoSerializer(photo).data)()

    @staticmethod
    @handle_exceptions("Фотография")
    @sync_to_async
    def delete_photo(photo_id: int) -> int:
        """
        Удаление фотографии вместе с файлом в media (см. Photo.delete)
        :param photo_id: ID фотографии
        :return: ID удаленной фотографии
        """
        photo = Photo.objects.get(pk=photo_id)
        photo.delete()
        return photo_id
