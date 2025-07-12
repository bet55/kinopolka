from django.db import models
from django.core.exceptions import ValidationError
import os


class Ingredient(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Название ингредиента'
    )
    is_available = models.BooleanField(
        default=False,
        verbose_name='Наличие'
    )
    image = models.ImageField(
        upload_to='media/ingredients/',
        blank=True,
        null=True,
        default='media/ingredients/default.png',
        verbose_name='Изображение'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        # Delete associated image if it exists and is not the default image
        if self.image and 'default.png' not in self.image.name:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        if self.cocktail_ingredients.exists():
            raise ValidationError(
                "Нельзя удалить ингредиент, который используется в коктейлях. "
                "Сначала удалите связанные коктейли."
            )
        super().delete(*args, **kwargs)


class Cocktail(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Название коктейля'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='CocktailIngredient',
        related_name='cocktails',
        verbose_name='Ингредиенты'
    )
    instructions = models.TextField(
        verbose_name='Инструкция приготовления'
    )
    image = models.ImageField(
        upload_to='media/cocktails/',
        blank=True,
        null=True,
        default='media/cocktails/default.png',
        verbose_name='Изображение коктейля'
    )

    class Meta:
        verbose_name = 'Коктейль'
        verbose_name_plural = 'Коктейли'
        ordering = ['name']

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        # Delete associated image if it exists and is not the default image
        if self.image and 'default.png' not in self.image.name:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super().delete(*args, **kwargs)

    @property
    def is_available(self):
        """Проверяет, все ли ингредиенты коктейля доступны"""
        if not self.ingredients.exists():
            return False

        return all(
            ci.ingredient.is_available
            for ci in self.ingredient_amounts.all()
        )

    def get_availability_display(self):
        """Возвращает текстовое представление доступности"""
        return "Доступен" if self.is_available else "Недоступен"


class CocktailIngredient(models.Model):
    MEASUREMENT_UNITS = [
        ('ml', 'миллилитры'),
        ('g', 'граммы'),
        ('pcs', 'штуки'),
        ('pinch', 'щепотка'),
        ('slice', 'долька'),
    ]

    cocktail = models.ForeignKey(
        'Cocktail',
        on_delete=models.CASCADE,
        related_name='ingredient_amounts',
        verbose_name='Коктейль'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        related_name='cocktail_ingredients',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        default=1
    )
    unit = models.CharField(
        max_length=10,
        choices=MEASUREMENT_UNITS,
        default='ml',
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент коктейля'
        verbose_name_plural = 'Ингредиенты коктейлей'
        unique_together = [['cocktail', 'ingredient']]

    def __str__(self):
        return f"{self.amount} {self.get_unit_display()} {self.ingredient.name}"
