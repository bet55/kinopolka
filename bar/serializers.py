from rest_framework import serializers
from .models import Ingredient, Cocktail, CocktailIngredient


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'is_available', 'image']
        extra_kwargs = {
            'image': {'required': False, 'allow_null': True}
        }


class CocktailIngredientSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer()
    unit_display = serializers.CharField(source='get_unit_display', read_only=True)

    class Meta:
        model = CocktailIngredient
        fields = ['ingredient', 'amount', 'unit', 'unit_display']


class CocktailSerializer(serializers.ModelSerializer):
    ingredients = CocktailIngredientSerializer(
        source='ingredient_amounts',
        many=True,
        read_only=True
    )
    is_available = serializers.SerializerMethodField()

    class Meta:
        model = Cocktail
        fields = [
            'id',
            'name',
            'instructions',
            'image',
            'is_available',
            'ingredients',
        ]
        extra_kwargs = {
            'image': {'required': False, 'allow_null': True}
        }

    def get_is_available(self, obj):
        """Метод для получения значения is_available"""
        return obj.is_available


class CocktailCreateUpdateSerializer(serializers.ModelSerializer):
    ingredients = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Cocktail
        fields = [
            'name',
            'instructions',
            'image',
            'ingredients'
        ]

    def validate_ingredients(self, value):
        for item in value:
            if 'ingredient' not in item:
                raise serializers.ValidationError("Каждый ингредиент должен содержать ID ингредиента")
        return value
