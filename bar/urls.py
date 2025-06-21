from django.urls import path
from .views import (
    IngredientListCreateAPIView,
    IngredientDetailAPIView,
    CocktailListCreateAPIView,
    CocktailDetailAPIView,
    CocktailAvailabilityAPIView
)

urlpatterns = [
    # Ингредиенты
    path('ingredients/', IngredientListCreateAPIView.as_view()),
    path('ingredients/<int:pk>/', IngredientDetailAPIView.as_view()),

    # Коктейли
    path('cocktails/', CocktailListCreateAPIView.as_view()),
    path('cocktails/<int:pk>/', CocktailDetailAPIView.as_view()),
    path('cocktails/<int:pk>/availability/', CocktailAvailabilityAPIView.as_view()),
]