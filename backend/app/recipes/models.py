import datetime

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.forms import ModelChoiceField
from core.models import CreatedModel
from users.models import User


class Subscribe(models.Model):
    """Model subscribe."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )
    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique follow',
            )
        ]

class Ingredient(models.Model):
    """Model Ingredient."""
    name = models.CharField(max_length=200, unique=True)
    measurement_unit = models.CharField(max_length=20, unique=True)


class Tag(models.Model):
    """Model Tag."""
    name = models.CharField(max_length=200, unique=True)
    color = models.CharField(max_length=7, unique=True)
    slug = models.SlugField(
        max_length=200,
        verbose_name='Слаг',
        unique=True
    )


class Recipe(CreatedModel):
    """Model Recipe."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор публикации',
        blank=False
    )
    name = models.TextField(
        verbose_name='Название рецепта',
        blank=False
    )
    image = models.ImageField(
        'Картинка',
        upload_to='recipes/',
        blank=False
    )
    text = models.TextField(
        verbose_name='Текстовое описание',
        blank=False
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='QuantityIngredient',
        verbose_name='Ингридиенты',
        related_name='recipes',
        blank=False
        )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги',
        related_name='tags',
        blank=False
        )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления в минутах',
        validators=MinValueValidator(
            1, 'Минимальное время приготовления 1 минута!')
        )

    def __str__(self):
        return self.text[:15]

class QuantityIngredient(models.Model):
    """Table for quantity ingredient."""
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингридиент',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    quantity = models.IntegerField(
        verbose_name='Количество ингридиентов'
    )

class Favorite(models.Model):
    """Favorite recipes."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт'
    )


class Cart(models.Model):
    """Model for buy."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Корзина'
    )
