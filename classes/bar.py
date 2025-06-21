from django.core.exceptions import ValidationError

from bar.models import Ingredient, Cocktail, CocktailIngredient


class IngredientHandler:
    @staticmethod
    def create_ingredient(name, is_available=False, image=None):
        """
        Создание нового ингредиента
        """
        try:
            ingredient = Ingredient.objects.create(
                name=name,
                is_available=is_available,
                image=image
            )
            return ingredient
        except Exception as e:
            raise ValidationError(f"Ошибка при создании ингредиента: {str(e)}")

    @staticmethod
    def get_all_ingredients():
        """
        Получение всех ингредиентов
        """
        return Ingredient.objects.all().order_by('name')

    @staticmethod
    def get_ingredient_by_id(ingredient_id):
        """
        Получение ингредиента по ID
        """
        try:
            return Ingredient.objects.get(pk=ingredient_id)
        except Ingredient.DoesNotExist:
            raise ValidationError("Ингредиент с указанным ID не найден")

    @staticmethod
    def update_ingredient(ingredient_id, **kwargs):
        """
        Обновление ингредиента
        """
        ingredient = IngredientHandler.get_ingredient_by_id(ingredient_id)
        for key, value in kwargs.items():
            setattr(ingredient, key, value)
        ingredient.save()
        return ingredient

    @staticmethod
    def delete_ingredient(ingredient_id):
        """
        Удаление ингредиента (с проверкой на использование в коктейлях)
        """
        ingredient = IngredientHandler.get_ingredient_by_id(ingredient_id)
        ingredient.delete()
        return True

    @staticmethod
    def get_ingredient_availability(ingredient_id):
        """
        Получение статуса доступности ингредиента
        """
        ingredient = IngredientHandler.get_ingredient_by_id(ingredient_id)
        return ingredient.is_available


class CocktailHandler:
    @staticmethod
    def create_cocktail(name, instructions, image=None, ingredients=None):
        """
        Создание нового коктейля с существующими ингредиентами
        :param name: Название коктейля
        :param instructions: Инструкция приготовления
        :param image: Изображение коктейля (опционально)
        :param ingredients: Список словарей с ингредиентами вида:
            [{
                'ingredient': ID_ингредиента,
                'amount': количество,
                'unit': единица_измерения
            }]
        :return: Созданный коктейль
        :raises: ValidationError если ингредиент не найден
        """
        try:
            # Создаем сам коктейль
            cocktail = Cocktail.objects.create(
                name=name,
                instructions=instructions,
                image=image
            )

            # Добавляем ингредиенты если они переданы
            if ingredients:
                for ingredient_data in ingredients:
                    # Проверяем что ингредиент существует
                    ingredient_id = ingredient_data['ingredient']
                    try:
                        ingredient = Ingredient.objects.get(pk=ingredient_id)
                    except Ingredient.DoesNotExist:
                        raise ValidationError(f"Ингредиент с ID {ingredient_id} не найден")

                    # Создаем связь коктейля с ингредиентом
                    CocktailIngredient.objects.create(
                        cocktail=cocktail,
                        ingredient=ingredient,
                        amount=ingredient_data.get('amount', 1),
                        unit=ingredient_data.get('unit', 'ml')
                    )

            return cocktail

        except Exception as e:
            # Если что-то пошло не так, откатываем изменения
            if 'cocktail' in locals():
                cocktail.delete()
            raise ValidationError(f"Ошибка при создании коктейля: {str(e)}")

    @staticmethod
    def get_all_cocktails():
        """
        Получение всех коктейлей с предзагрузкой ингредиентов
        """
        return Cocktail.objects.prefetch_related('ingredient_amounts__ingredient').all().order_by('name')

    @staticmethod
    def get_cocktail_by_id(cocktail_id):
        """
        Получение коктейля по ID с предзагрузкой ингредиентов
        """
        try:
            return Cocktail.objects.prefetch_related('ingredient_amounts__ingredient').get(pk=cocktail_id)
        except Cocktail.DoesNotExist:
            raise ValidationError("Коктейль с указанным ID не найден")

    @staticmethod
    def update_cocktail(cocktail_id, **kwargs):
        """
        Обновление коктейля
        """
        cocktail = CocktailHandler.get_cocktail_by_id(cocktail_id)
        ingredients = kwargs.pop('ingredients', None)

        for key, value in kwargs.items():
            setattr(cocktail, key, value)
        cocktail.save()

        if ingredients is not None:
            # Обновляем ингредиенты
            cocktail.ingredient_amounts.all().delete()
            for ingredient_data in ingredients:
                CocktailIngredient.objects.create(
                    cocktail=cocktail,
                    ingredient=ingredient_data['ingredient'],
                    amount=ingredient_data.get('amount', 1),
                    unit=ingredient_data.get('unit', 'ml')
                )

        return cocktail

    @staticmethod
    def delete_cocktail(cocktail_id):
        """
        Удаление коктейля
        """
        cocktail = CocktailHandler.get_cocktail_by_id(cocktail_id)
        cocktail.delete()
        return True

    @staticmethod
    def get_cocktail_availability(cocktail_id):
        """
        Получение статуса доступности коктейля
        """
        cocktail = CocktailHandler.get_cocktail_by_id(cocktail_id)
        return cocktail.is_available

    @staticmethod
    def get_cocktail_ingredients(cocktail_id):
        """
        Получение всех ингредиентов коктейля с количеством
        """
        cocktail = CocktailHandler.get_cocktail_by_id(cocktail_id)
        return cocktail.ingredient_amounts.all().select_related('ingredient')
