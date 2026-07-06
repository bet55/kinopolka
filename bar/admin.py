from django.contrib import admin

from bar.models import Cocktail, CocktailIngredient, Ingredient


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ["name", "is_available"]
    list_editable = ["is_available"]


class CocktailIngredientInline(admin.TabularInline):
    model = CocktailIngredient
    extra = 1


@admin.register(Cocktail)
class CocktailAdmin(admin.ModelAdmin):
    list_display = ["name", "get_availability_display"]
    inlines = [CocktailIngredientInline]
