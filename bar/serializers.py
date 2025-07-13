from rest_framework import serializers
import json
from .models import Ingredient, Cocktail, CocktailIngredient


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'is_available', 'image']
        extra_kwargs = {
            'image': {'required': False, 'allow_null': True}
        }

    def validate_image(self, value):
        if not value:
            return None
        return value


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

    def validate_image(self, value):
        if not value:
            return None
        return value

    def get_is_available(self, obj):
        return obj.is_available


class CocktailCreateUpdateSerializer(serializers.ModelSerializer):
    ingredients = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Cocktail
        fields = [
            'name',
            'instructions',
            'image',
            'ingredients'
        ]

    def validate_ingredients(self, value):
        if not value:
            return []
        try:
            ingredients = json.loads(value)
            if not isinstance(ingredients, list):
                raise serializers.ValidationError("Поле ingredients должно быть списком")
            for item in ingredients:
                if not isinstance(item, dict) or 'ingredient' not in item:
                    raise serializers.ValidationError("Каждый ингредиент должен быть словарем и содержать поле 'ingredient'")
                try:
                    ingredient_id = int(item['ingredient'])
                    Ingredient.objects.get(pk=ingredient_id)
                    item['ingredient'] = ingredient_id
                except (ValueError, TypeError):
                    raise serializers.ValidationError(f"ID ингредиента '{item['ingredient']}' должен быть числом")
                except Ingredient.DoesNotExist:
                    raise serializers.ValidationError(f"Ингредиент с ID {item['ingredient']} не существует")
                try:
                    item['amount'] = int(item['amount'])
                    if item['amount'] <= 0:
                        raise serializers.ValidationError(f"Количество для ингредиента '{item['ingredient']}' должно быть положительным")
                except (ValueError, TypeError):
                    raise serializers.ValidationError(f"Количество для ингредиента '{item['ingredient']}' должно быть числом")
                valid_units = [choice[0] for choice in CocktailIngredient.MEASUREMENT_UNITS]
                if item.get('unit') and item['unit'] not in valid_units:
                    raise serializers.ValidationError(f"Единица измерения '{item['unit']}' недопустима")
            return ingredients
        except json.JSONDecodeError:
            raise serializers.ValidationError("Невалидный формат JSON в поле ingredients")

    def validate_image(self, value):
        if not value:
            return None
        return value