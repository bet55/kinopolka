import logging
from django.core.exceptions import ValidationError
from django.db import transaction
from bar.models import Ingredient
from bar.serializers import IngredientSerializer
from .exception_handler import handle_exceptions
from functools import wraps

# Configure logger
logger = logging.getLogger('kinopolka')



class IngredientHandler:
    @staticmethod
    @handle_exceptions("Ингредиент")
    @transaction.atomic
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
    def get_all_ingredients() -> list[dict]:
        """
        Получение всех ингредиентов
        :return: список сериализованных ингредиентов
        """
        ingredients = Ingredient.objects.all()
        return IngredientSerializer(ingredients, many=True).data

    @staticmethod
    @handle_exceptions("Ингредиент")
    def get_ingredient_by_id(ingredient_id: int) -> dict:
        """
        Получение ингредиента по ID
        :param ingredient_id: ID ингредиента
        :return: сериализованные данные ингредиента
        """
        ingredient = Ingredient.objects.get(pk=ingredient_id)
        return IngredientSerializer(ingredient).data

    @staticmethod
    @handle_exceptions("Ингредиент")
    @transaction.atomic
    def update_ingredient(ingredient_id: int, data: dict, request=None) -> dict:
        """
        Обновление ингредиента
        :param ingredient_id: ID ингредиента
        :param data: словарь с обновленными данными
        :param request: HTTP-запрос для контекста сериализатора
        :return: сериализованные данные ингредиента
        """
        ingredient = Ingredient.objects.get(pk=ingredient_id)
        serializer = IngredientSerializer(ingredient, data=data, partial=True, context={'request': request})
        if not serializer.is_valid():
            raise ValidationError(f"Невалидные данные: {serializer.errors}")
        updated_ingredient = serializer.save()
        return IngredientSerializer(updated_ingredient).data

    @staticmethod
    @handle_exceptions("Ингредиент")
    def delete_ingredient(ingredient_id: int) -> int:
        """
        Удаление ингредиента (с проверкой на использование в коктейлях)
        :param ingredient_id: ID ингредиента
        :return: ID удаленного ингредиента
        """
        ingredient = Ingredient.objects.get(pk=ingredient_id)
        ingredient.delete()
        return ingredient_id

    @staticmethod
    @handle_exceptions("Ингредиент")
    def get_ingredient_availability(ingredient_id: int) -> bool:
        """
        Получение статуса доступности ингредиента
        :param ingredient_id: ID ингредиента
        :return: статус (True/False) наличия
        """
        ingredient = Ingredient.objects.get(pk=ingredient_id)
        return ingredient.is_available