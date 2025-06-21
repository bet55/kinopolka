from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError

from classes.bar import IngredientHandler, CocktailHandler
from .serializers import (
    IngredientSerializer,
    CocktailSerializer,
    CocktailCreateUpdateSerializer
)


class IngredientListCreateAPIView(APIView):
    def get(self, request):
        ingredients = IngredientHandler.get_all_ingredients()
        serializer = IngredientSerializer(ingredients, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = IngredientSerializer(data=request.data)
        if serializer.is_valid():
            try:
                ingredient = IngredientHandler.create_ingredient(
                    name=serializer.validated_data['name'],
                    is_available=serializer.validated_data.get('is_available', False),
                    image=serializer.validated_data.get('image')
                )
                return Response(
                    IngredientSerializer(ingredient).data,
                    status=status.HTTP_201_CREATED
                )
            except ValidationError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class IngredientDetailAPIView(APIView):
    def get(self, request, pk):
        try:
            ingredient = IngredientHandler.get_ingredient_by_id(pk)
            serializer = IngredientSerializer(ingredient)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

    def put(self, request, pk):
        try:
            ingredient = IngredientHandler.get_ingredient_by_id(pk)
            serializer = IngredientSerializer(ingredient, data=request.data)
            if serializer.is_valid():
                updated_ingredient = IngredientHandler.update_ingredient(
                    pk,
                    **serializer.validated_data
                )
                return Response(IngredientSerializer(updated_ingredient).data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, pk):
        try:
            IngredientHandler.delete_ingredient(pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class CocktailListCreateAPIView(APIView):
    def get(self, request):
        cocktails = CocktailHandler.get_all_cocktails()
        serializer = CocktailSerializer(cocktails, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CocktailCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                cocktail = CocktailHandler.create_cocktail(
                    name=serializer.validated_data['name'],
                    instructions=serializer.validated_data['instructions'],
                    image=serializer.validated_data.get('image'),
                    ingredients=serializer.validated_data.get('ingredients', [])
                )
                return Response(
                    CocktailSerializer(cocktail).data,
                    status=status.HTTP_201_CREATED
                )
            except ValidationError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CocktailDetailAPIView(APIView):
    def get(self, request, pk):
        try:
            cocktail = CocktailHandler.get_cocktail_by_id(pk)
            serializer = CocktailSerializer(cocktail)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

    def put(self, request, pk):
        try:
            cocktail = CocktailHandler.get_cocktail_by_id(pk)
            serializer = CocktailCreateUpdateSerializer(cocktail, data=request.data)
            if serializer.is_valid():
                updated_cocktail = CocktailHandler.update_cocktail(
                    pk,
                    **serializer.validated_data
                )
                return Response(CocktailSerializer(updated_cocktail).data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, pk):
        try:
            CocktailHandler.delete_cocktail(pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class CocktailAvailabilityAPIView(APIView):
    def get(self, request, pk):
        try:
            is_available = CocktailHandler.get_cocktail_availability(pk)
            return Response({'is_available': is_available})
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
