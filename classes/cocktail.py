import logging
from django.core.exceptions import ValidationError
from django.db import transaction
from bar.models import Ingredient, Cocktail, CocktailIngredient
from bar.serializers import CocktailSerializer, CocktailCreateUpdateSerializer, CocktailIngredientSerializer
from .exception_handler import handle_exceptions

# Configure logger
logger = logging.getLogger('kinopolka')


class CocktailHandler:
    @staticmethod
    @handle_exceptions("Коктейль")
    @transaction.atomic
    def create_cocktail(data: dict, request=None) -> dict:
        """
        Создание нового коктейля с существующими ингредиентами
        :param data: словарь с данными (name, instructions, image, ingredients)
        :param request: HTTP-запрос для контекста сериализатора
        :return: сериализованные данные коктейля
        """
        print(data)
        if not data.get('name'):
            raise ValidationError("Поле 'name' обязательно")
        serializer = CocktailCreateUpdateSerializer(data=data, context={'request': request})
        if not serializer.is_valid():
            raise ValidationError(f"Невалидные данные: {serializer.errors}")

        validated_data = serializer.validated_data
        cocktail = Cocktail.objects.create(
            name=validated_data['name'],
            instructions=validated_data['instructions'],
            image=validated_data.get('image')
        )

        for ingredient_data in validated_data.get('ingredients', []):
            ingredient = Ingredient.objects.get(pk=ingredient_data['ingredient'])
            CocktailIngredient.objects.create(
                cocktail=cocktail,
                ingredient=ingredient,
                amount=ingredient_data.get('amount', 1),
                unit=ingredient_data.get('unit', 'ml')
            )

        return CocktailSerializer(cocktail).data

    @staticmethod
    @handle_exceptions("Коктейли")
    def get_all_cocktails() -> list[dict]:
        """
        Получение всех коктейлей с предзагрузкой ингредиентов
        :return: список сериализованных коктейлей
        """
        cocktails = Cocktail.objects.all().prefetch_related('ingredients')
        # cocktails = Cocktail.objects.prefetch_related(
        #     'ingredient_amounts__ingredient'
        # ).select_related('image').all().order_by('name')

        return CocktailSerializer(cocktails, many=True).data

    @staticmethod
    @handle_exceptions("Коктейль")
    def get_cocktail_by_id(cocktail_id: int) -> dict:
        """
        Получение коктейля по ID с предзагрузкой ингредиентов
        :param cocktail_id: ID коктейля
        :return: сериализованные данные коктейля
        """
        cocktail = Cocktail.objects.prefetch_related(
            'ingredient_amounts__ingredient'
        ).select_related('image').get(pk=cocktail_id)
        return CocktailSerializer(cocktail).data

    @staticmethod
    @handle_exceptions("Коктейль")
    @transaction.atomic
    def update_cocktail(cocktail_id: int, data: dict, request=None) -> dict:
        """
        Обновление коктейля
        :param cocktail_id: ID коктейля
        :param data: словарь с обновленными данными (name, instructions, image, ingredients)
        :param request: HTTP-запрос для контекста сериализатора
        :return: сериализованные данные коктейля
        """
        cocktail = Cocktail.objects.get(pk=cocktail_id)
        old_image = cocktail.image.name if cocktail.image else None
        serializer = CocktailCreateUpdateSerializer(cocktail, data=data, partial=True, context={'request': request})
        if not serializer.is_valid():
            raise ValidationError(f"Невалидные данные: {serializer.errors}")

        validated_data = serializer.validated_data
        for field, value in validated_data.items():
            if field != 'ingredients':
                setattr(cocktail, field, value)
        cocktail.save()

        if 'ingredients' in validated_data:
            cocktail.ingredient_amounts.all().delete()
            for ingredient_data in validated_data['ingredients']:
                ingredient = Ingredient.objects.get(pk=ingredient_data['ingredient'])
                CocktailIngredient.objects.create(
                    cocktail=cocktail,
                    ingredient=ingredient,
                    amount=ingredient_data.get('amount', 1),
                    unit=ingredient_data.get('unit', 'ml')
                )

        # Delete old image if it was changed and is not the default image
        if old_image and old_image != cocktail.image.name and old_image != 'media/default.png':
            import os
            if os.path.isfile(old_image):
                os.remove(old_image)

        return CocktailSerializer(cocktail).data

    @staticmethod
    @handle_exceptions("Коктейль")
    def delete_cocktail(cocktail_id: int) -> int:
        """
        Удаление коктейля
        :param cocktail_id: ID коктейля
        :return: ID удаленного коктейля
        """
        cocktail = Cocktail.objects.get(pk=cocktail_id)
        cocktail.delete()
        return cocktail_id

    @staticmethod
    @handle_exceptions("Коктейль")
    def get_cocktail_availability(cocktail_id: int) -> bool:
        """
        Получение статуса доступности коктейля
        :param cocktail_id: ID коктейля
        :return: статус доступности (True/False)
        """
        cocktail = Cocktail.objects.get(pk=cocktail_id)
        return cocktail.is_available

    @staticmethod
    @handle_exceptions("Ингредиенты коктейля")
    def get_cocktail_ingredients(cocktail_id: int) -> list[dict]:
        """
        Получение всех ингредиентов коктейля с количеством
        :param cocktail_id: ID коктейля
        :return: список сериализованных ингредиентов
        """
        cocktail = Cocktail.objects.get(pk=cocktail_id)
        ingredients = cocktail.ingredient_amounts.all().select_related('ingredient')
        return CocktailIngredientSerializer(ingredients, many=True).data
