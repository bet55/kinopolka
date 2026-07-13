# tests.py
from django.test import TestCase

from bar.models import Ingredient
from classes import IngredientHandler


class IngredientHandlerTests(TestCase):
    async def test_get_ingredient_by_id(self) -> None:
        ingredient = await Ingredient.objects.acreate(name="Лайм", is_available=True)
        result = await IngredientHandler.get_ingredient_by_id(ingredient.id)
        self.assertEqual(result["name"], "Лайм")
        self.assertTrue(result["is_available"])

    async def test_get_ingredient_by_id_not_found(self) -> None:
        # handle_exceptions переводит ObjectDoesNotExist в error-dict, не поднимая исключение
        result = await IngredientHandler.get_ingredient_by_id(999)
        self.assertEqual(result["error"]["status"], 404)
        self.assertEqual(result["error"]["message"], "Запрашиваемый объект не найден")
