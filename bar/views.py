from django.shortcuts import render
from adrf.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from classes import CocktailHandler, IngredientHandler, Error, Telegram
from mixins import GlobalDataMixin
from asgiref.sync import sync_to_async


def handle_response(data, success_status=status.HTTP_200_OK):
    if isinstance(data, Error):
        return Response({'error': data.message}, status=data.status)
    return Response(data, status=success_status)


class IngredientTelegramRequest(APIView):
    async def post(self, request: Request):
        tg = Telegram()
        if not tg.is_init:
            return Response({'error': 'Не подключились'}, status=400)

        text = request.data.get('text', 'а где текст?')

        good_message = await tg.send_message(text)
        return Response({'message': good_message}, status=200)


class Bar(GlobalDataMixin, APIView):
    async def get(self, request: Request):
        """
        Получение заполненности бара (коктейли + ингредиенты)
        """
        ingredients = await IngredientHandler.get_all_ingredients()
        cocktails = await CocktailHandler.get_all_cocktails()

        errors = [e.message for e in [ingredients, cocktails] if isinstance(e, Error)]
        if errors:
            return Response({'error': '\n'.join(errors)}, status=status.HTTP_400_BAD_REQUEST)

        context = {'cocktails': cocktails, 'ingredients': ingredients}
        return render(request, "bar.html", context=await self.add_context_data(request, context))


class IngredientDetail(APIView):
    async def get(self, request: Request, pk: int):
        """
        Получение ингредиента по ID
        """
        ingredient = await IngredientHandler.get_ingredient_by_id(pk)
        return handle_response(ingredient)

    async def put(self, request: Request, pk: int):
        """
        Обновление ингредиента по ID
        """
        ingredient = await IngredientHandler.update_ingredient(pk, request.data, request)
        return handle_response(ingredient)

    async def delete(self, request: Request, pk: int):
        """
        Удаление ингредиента по ID
        """
        response_id = await IngredientHandler.delete_ingredient(pk)
        return handle_response(response_id, status.HTTP_204_NO_CONTENT)


class IngredientListCreate(APIView):
    async def get(self, request: Request):
        """
        Получение всех ингредиентов
        """
        ingredient = await IngredientHandler.get_all_ingredients()
        return handle_response(ingredient)

    async def post(self, request: Request):
        """
        Создание нового ингредиента
        """
        ingredient = await IngredientHandler.create_ingredient(request.data, request)
        return handle_response(ingredient, status.HTTP_201_CREATED)


class CocktailDetail(APIView):
    async def get(self, request: Request, pk: int):
        """
        Получение коктейля по ID
        """
        cocktail = await CocktailHandler.get_cocktail_by_id(pk)
        return handle_response(cocktail)

    async def put(self, request: Request, pk: int):
        """
        Обновление коктейля по ID
        """
        cocktail = await CocktailHandler.update_cocktail(pk, request.data, request)
        return handle_response(cocktail)

    async def delete(self, request: Request, pk: int):
        """
        Удаление коктейля по ID
        """
        response_id = await CocktailHandler.delete_cocktail(pk)
        return handle_response(response_id, status.HTTP_204_NO_CONTENT)


class CocktailListCreate(APIView):
    async def get(self, request: Request):
        """
        Получение списка всех коктейлей
        """
        cocktails = await CocktailHandler.get_all_cocktails()
        return handle_response(cocktails)

    async def post(self, request: Request):
        """
        Создание нового коктейля
        """
        cocktail = await CocktailHandler.create_cocktail(request.data, request)
        return handle_response(cocktail, status.HTTP_201_CREATED)


class CocktailAvailability(APIView):
    async def get(self, request: Request, pk: int):
        """
        Получение статуса доступности коктейля
        """
        is_available = await CocktailHandler.get_cocktail_availability(pk)
        return handle_response(is_available)
