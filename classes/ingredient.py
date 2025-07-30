import logging
from rest_framework.exceptions import ValidationError
from bar.models import Ingredient
from bar.serializers import IngredientSerializer
from utils.exception_handler import handle_exceptions
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)



class IngredientHandler:

    @staticmethod
    @handle_exceptions("Ингредиент")
    @sync_to_async
    def create_ingredient(data: dict, request=None) -> dict:
        """
        Создание нового ингредиента
        :param data: словарь с данными (name, is_available, image)
        :param request: HTTP-запрос для контекста сериализатора
        :return: сериализованные данные ингредиента
        """
        if not data.get('name'):
            raise ValidationError("Поле 'name' обязательно")

        serializer = IngredientSerializer(data=data, context={'request': request})
        if not serializer.is_valid():
            raise ValidationError(f"Невалидные данные: {serializer.errors}")

        ingredient = serializer.save()
        return IngredientSerializer(ingredient).data

    @staticmethod
    @handle_exceptions("Ингредиенты")
    @sync_to_async
    def get_all_ingredients() -> list[dict]:
        """
        Получение всех ингредиентов
        :return: список сериализованных ингредиентов
        """
        ingredients = Ingredient.objects.all()
        return IngredientSerializer(ingredients, many=True).data

    @staticmethod
    @handle_exceptions("Ингредиент")
    async def get_ingredient_by_id(ingredient_id: int) -> dict:
        """
        Получение ингредиента по ID
        :param ingredient_id: ID ингредиента
        :return: сериализованные данные ингредиента
        """
        ingredient = Ingredient.objects.aget(pk=ingredient_id)
        return IngredientSerializer(ingredient).data

    @staticmethod
    @handle_exceptions("Ингредиент")
    async def update_ingredient(ingredient_id: int, data: dict, request=None) -> dict:
        """
        Обновление ингредиента
        :param ingredient_id: ID ингредиента
        :param data: словарь с обновленными данными
        :param request: HTTP-запрос для контекста сериализатора
        :return: сериализованные данные ингредиента
        """
        ingredient = await Ingredient.objects.aget(pk=ingredient_id)
        old_image = ingredient.image.name if ingredient.image else None
        serializer = IngredientSerializer(ingredient, data=data, partial=True, context={'request': request})

        if not await sync_to_async(serializer.is_valid)():
            raise ValidationError(f"Невалидные данные: {serializer.errors}")

        validated_data = serializer.validated_data
        for field, value in validated_data.items():
            setattr(ingredient, field, value)

        await ingredient.asave()

        if old_image and old_image != ingredient.image.name and 'default.png' not in old_image:
            import os
            if os.path.isfile(old_image):
                os.remove(old_image)

        return IngredientSerializer(ingredient).data

    @staticmethod
    @handle_exceptions("Ингредиент")
    async def delete_ingredient(ingredient_id: int) -> int:
        """
        Удаление ингредиента (с проверкой на использование в коктейлях)
        :param ingredient_id: ID ингредиента
        :return: ID удаленного ингредиента
        """
        ingredient = await Ingredient.objects.aget(pk=ingredient_id)
        await ingredient.adelete()
        return ingredient_id

    @staticmethod
    @handle_exceptions("Ингредиент")
    async def get_ingredient_availability(ingredient_id: int) -> bool:
        """
        Получение статуса доступности ингредиента
        :param ingredient_id: ID ингредиента
        :return: статус (True/False) наличия
        """
        ingredient = await Ingredient.objects.aget(pk=ingredient_id)
        return ingredient.is_available
