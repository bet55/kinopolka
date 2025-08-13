# tests.py
from django.test import TestCase

from classes import Error, IngredientHandler


class IngredientHandlerTests(TestCase):
    def test_get_ingredient_by_id_not_found(self):
        result = IngredientHandler.get_ingredient_by_id(999)
        self.assertIsInstance(result, Error)
        self.assertEqual(result.status, 404)
        self.assertEqual(result.message, "Ингредиент не найден")
