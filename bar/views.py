from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status

from classes import CocktailHandler, IngredientHandler, Error


def handle_response(data, success_status=status.HTTP_200_OK):
    if isinstance(data, Error):
        return Response({'error': data.message}, status=data.status)
    return Response(data, status=success_status)


class Bar(APIView):
    def get(self, request: Request):
        """
        Получение заполненности бара (коктейли + ингредиенты)
        """
        ingredients = IngredientHandler.get_all_ingredients()
        cocktails = CocktailHandler.get_all_cocktails()

        errors = [e.message for e in [ingredients, cocktails] if isinstance(e, Error)]
        if errors:
            return Response({'error': '\n'.join(errors)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'cocktails': cocktails, 'ingredients': ingredients})


class IngredientDetail(APIView):
    def get(self, request: Request, pk: int):
        """
        Получение ингредиента по ID
        """
        ingredient = IngredientHandler.get_ingredient_by_id(pk)
        return handle_response(ingredient)

    def put(self, request: Request, pk: int):
        """
        Обновление ингредиента по ID
        """
        ingredient = IngredientHandler.update_ingredient(pk, request.data, request)
        return handle_response(ingredient)

    def delete(self, request: Request, pk: int):
        """
        Удаление ингредиента по ID
        """
        response_id = IngredientHandler.delete_ingredient(pk)
        return handle_response(response_id, status.HTTP_204_NO_CONTENT)


class IngredientListCreate(APIView):
    def get(self, request: Request):
        """
        Получение всех ингредиентов
        """
        ingredient = IngredientHandler.get_all_ingredients()
        return handle_response(ingredient)

    def post(self, request: Request):
        """
        Создание нового ингредиента
        """
        ingredient = IngredientHandler.create_ingredient(request.data, request)
        return handle_response(ingredient, status.HTTP_201_CREATED)


class CocktailDetail(APIView):
    def get(self, request: Request, pk: int):
        """
        Получение коктейля по ID
        """
        cocktail = CocktailHandler.get_cocktail_by_id(pk)
        return handle_response(cocktail)

    def put(self, request: Request, pk: int):
        """
        Обновление коктейля по ID
        """
        cocktail = CocktailHandler.update_cocktail(pk, request.data, request)
        return handle_response(cocktail)

    def delete(self, request: Request, pk: int):
        """
        Удаление коктейля по ID
        """
        response_id = CocktailHandler.delete_cocktail(pk)
        return handle_response(response_id, status.HTTP_204_NO_CONTENT)



class CocktailListCreate(APIView):
    def get(self, request: Request):
        """
        Получение списка всех коктейлей
        """
        cocktails = CocktailHandler.get_all_cocktails()
        return handle_response(cocktails)


    def post(self, request: Request):
        """
        Создание нового коктейля
        """
        cocktail = CocktailHandler.create_cocktail(request.data, request)
        return handle_response(cocktail, status.HTTP_201_CREATED)



class CocktailAvailability(APIView):
    def get(self, request: Request, pk: int):
        """
        Получение статуса доступности коктейля
        """
        is_available = CocktailHandler.get_cocktail_availability(pk)
        return handle_response(is_available)

