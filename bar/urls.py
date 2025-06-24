from django.urls import path
from .views import (
    Bar,
    IngredientListCreate,
    IngredientDetail,
    CocktailListCreate,
    CocktailDetail,
    CocktailAvailability
)

urlpatterns = [
    # Ингредиенты
    path('', Bar.as_view(), name='bar'),
    path('ingredients/', IngredientListCreate.as_view(), name='ingredient'),
    path('ingredients/<int:pk>/', IngredientDetail.as_view(), name='ingredient-detail'),
    path('cocktails/', CocktailListCreate.as_view(), name='cocktail'),
    path('cocktails/<int:pk>/', CocktailDetail.as_view(), name='cocktail-detail'),
    path('cocktails/<int:pk>/availability/', CocktailAvailability.as_view(), name='cocktail-availability'),
]