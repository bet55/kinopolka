import logging
import os

from asgiref.sync import sync_to_async
from rest_framework.exceptions import ValidationError

from bar.models import Cocktail, CocktailIngredient, Ingredient
from bar.serializers import (
    CocktailCreateUpdateSerializer,
    CocktailIngredientSerializer,
    CocktailSerializer,
)
from utils.exception_handler import handle_exceptions


logger = logging.getLogger(__name__)


class CocktailHandler:
    @staticmethod
    @handle_exceptions("Коктейль")
    @sync_to_async
    def create_cocktail(data: dict, request=None) -> dict:
        """
        Создание нового коктейля с существующими ингредиентами
        :param data: словарь с данными (name, instructions, image, ingredients)
        :param request: HTTP-запрос для контекста сериализатора
        :return: сериализованные данные коктейля
        """
        if not data.get("name"):
            raise ValidationError("Поле 'name' обязательно")

        serializer = CocktailCreateUpdateSerializer(data=data, context={"request": request})
        if not serializer.is_valid():
            raise ValidationError(f"Невалидные данные: {serializer.errors}")

        validated_data = serializer.validated_data
        cocktail = Cocktail.objects.create(
            name=validated_data["name"],
            instructions=validated_data.get("instructions", ""),
            image=validated_data.get("image"),
        )

        for ingredient_data in validated_data.get("ingredients", []):
            ingredient = Ingredient.objects.get(pk=ingredient_data["ingredient"])
            CocktailIngredient.objects.create(
                cocktail=cocktail,
                ingredient=ingredient,
                amount=ingredient_data.get("amount", 1),
                unit=ingredient_data.get("unit", "ml"),
            )

        return CocktailSerializer(cocktail).data

    @staticmethod
    @handle_exceptions("Коктейли")
    @sync_to_async
    def get_all_cocktails() -> list[dict]:
        """
        Получение всех коктейлей с предзагрузкой ингредиентов
        :return: список сериализованных коктейлей
        """
        cocktails = Cocktail.objects.all().prefetch_related("ingredients")
        return CocktailSerializer(cocktails, many=True).data

    @staticmethod
    @handle_exceptions("Коктейль")
    async def get_cocktail_by_id(cocktail_id: int) -> dict:
        """
        Получение коктейля по ID с предзагрузкой ингредиентов
        :param cocktail_id: ID коктейля
        :return: сериализованные данные коктейля
        """
        cocktail = (
            await Cocktail.objects.prefetch_related("ingredient_amounts__ingredient")
            .select_related("image")
            .aget(pk=cocktail_id)
        )
        return CocktailSerializer(cocktail).data

    @staticmethod
    @handle_exceptions("Коктейль")
    async def update_cocktail(cocktail_id: int, data: dict, request=None) -> dict:
        """
        Обновление коктейля
        :param cocktail_id: ID коктейля
        :param data: словарь с обновленными данными
        :param request: HTTP-запрос для контекста сериализатора
        :return: сериализованные данные коктейля
        """
        cocktail = await Cocktail.objects.aget(pk=cocktail_id)
        old_image = cocktail.image.name if cocktail.image else None
        serializer = CocktailCreateUpdateSerializer(cocktail, data=data, partial=True, context={"request": request})

        if not await sync_to_async(serializer.is_valid)():
            raise ValidationError(f"Невалидные данные: {serializer.errors}")

        # Обновляем общие сведения
        validated_data = serializer.validated_data
        for field, value in validated_data.items():
            if field != "ingredients":
                setattr(cocktail, field, value)
        await cocktail.asave()

        # Обновляем ингредиенты
        await cocktail.ingredient_amounts.all().adelete()
        for ingredient_data in validated_data.get("ingredients", []):
            ingredient = await Ingredient.objects.aget(pk=ingredient_data["ingredient"])
            await CocktailIngredient.objects.acreate(
                cocktail=cocktail,
                ingredient=ingredient,
                amount=ingredient_data.get("amount", 1),
                unit=ingredient_data.get("unit", "ml"),
            )

        # Удаление старого изображения#
        if old_image != cocktail.image.name and old_image != "media/cocktails/default.png":
            if os.path.isfile(old_image):
                os.remove(old_image)

        serialized_data = await sync_to_async(lambda: CocktailSerializer(cocktail).data)()
        return serialized_data

    @staticmethod
    @handle_exceptions("Коктейль")
    async def delete_cocktail(cocktail_id: int) -> int:
        """
        Удаление коктейля
        :param cocktail_id: ID коктейля
        :return: ID удаленного коктейля
        """
        cocktail = await Cocktail.objects.aget(pk=cocktail_id)
        await cocktail.adelete()
        return cocktail_id

    @staticmethod
    @handle_exceptions("Коктейль")
    async def get_cocktail_availability(cocktail_id: int) -> bool:
        """
        Получение статуса доступности коктейля
        :param cocktail_id: ID коктейля
        :return: статус доступности (True/False)
        """
        cocktail = await Cocktail.objects.aget(pk=cocktail_id)
        return cocktail.is_available

    @staticmethod
    @handle_exceptions("Ингредиенты коктейля")
    async def get_cocktail_ingredients(cocktail_id: int) -> list[dict]:
        """
        Получение всех ингредиентов коктейля с количеством
        :param cocktail_id: ID коктейля
        :return: список сериализованных ингредиентов
        """
        cocktail = await Cocktail.objects.aget(pk=cocktail_id)
        ingredients = await cocktail.ingredient_amounts.all().select_related("ingredient")
        return CocktailIngredientSerializer(ingredients, many=True).data
