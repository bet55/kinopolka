from django.shortcuts import render
from adrf.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from classes import CocktailHandler, IngredientHandler, Telegram
from mixins import GlobalDataMixin
from utils.response_handler import handle_response


class IngredientTelegramRequest(APIView):
    async def post(self, request: Request):
        tg = Telegram()
        if not tg.is_init:
            return Response({'error': 'Не подключились'}, status=status.HTTP_500)

        text = request.data.get('text', 'а где текст?')

        good_message = await tg.send_message(text)
        return handle_response(good_message, {'message': good_message}, status.HTTP_200_OK)


class Bar(GlobalDataMixin, APIView):
    async def get(self, request: Request):
        """
        Получение заполненности бара (коктейли + ингредиенты)
        """
        ingredients = await IngredientHandler.get_all_ingredients()
        cocktails = await CocktailHandler.get_all_cocktails()


        context = {'cocktails': cocktails, 'ingredients': ingredients}

        response_format = request.query_params.get("format")
        if response_format == "json":
            return Response(
                context,
                status=status.HTTP_200_OK
            )


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
        return handle_response(response_id, status=status.HTTP_204_NO_CONTENT)


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
        return handle_response(ingredient, status=status.HTTP_201_CREATED)


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
        return handle_response(response_id, status=status.HTTP_204_NO_CONTENT)


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
