from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class Ingredient(models.Model):
    """Ingredient model. """
    name = models.CharField(
        max_length=200, db_index=True, verbose_name='Название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=200, verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    """ Tag model."""
    name = models.CharField(max_length=200, verbose_name='Название тега')
    color = models.CharField(max_length=7, null=True, verbose_name='Цвет')
    slug = models.SlugField(max_length=200, null=True, verbose_name='Slug')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """ Recipe model."""
    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author',
        verbose_name='Автор'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='AmountIngredientForRecipe',
        through_fields=('recipe', 'ingredient'),
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    name = models.CharField(
        max_length=200,
        db_index=True,
        verbose_name='Название'
    )
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Картинка')
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(
            1,
            message='Минимальное время готовки: 1 минута'
        )],
        verbose_name='Время приготовления'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class AmountIngredientForRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(
            1,
            message='Минимальное количество: 1 единица'
        )],
        verbose_name='Количество ингредиента'
    )

    class Meta:
        verbose_name = 'Количество ингредиента рецепта'
        verbose_name_plural = 'Количество ингредиентов рецепта'
        constraints = (
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique ingredients recipe'
            ),
        )


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_shopping_cart',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='user_shopping_cart',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = (
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart'
            ),
        )

    def __str__(self):
        return f'{self.name} , {self.recipe}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorited',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorited',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Избранный'
        verbose_name_plural = 'Избранные'
        constraints = (
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            ),
        )
