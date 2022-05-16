from django.core.validators import MinValueValidator
from django.db import models
from core.models import CreatedModel
from users.models import User


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
        through='IngredientRecipe',
        related_name='recipes',
        verbose_name='Продукты в рецепте',
        help_text='Выберите продукты рецепта')
    tags = models.ManyToManyField(
        Tag,
        through='TagRecipe',
        verbose_name='Тег рецепта',
        help_text='Выберите тег рецепта')
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления в минутах',
        validators=[MinValueValidator(
            limit_value=1,
            message='Минимальное время приготовления 1 минута!')])

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


class TagRecipe(models.Model):
    """Tag for recipe."""
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Теги',
        help_text='Выберите теги рецепта'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        help_text='Выберите рецепт')

    class Meta:
        """
        Мета параметры модели.
        """
        verbose_name = 'Теги рецепта'
        verbose_name_plural = 'Теги рецепта'
        constraints = [
            models.UniqueConstraint(fields=['tag', 'recipe'],
                                    name='unique_tagrecipe')
        ]

    def __str__(self):
        """"
        Метод строкового представления модели.
        """
        return f'{self.tag} {self.recipe}'


class IngredientRecipe(models.Model):
    """Ingredient for recipe."""
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredientrecipes',
        verbose_name='Продукты рецепта',
        help_text='Добавить продукты рецепта в корзину')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredientrecipes',
        verbose_name='Рецепт',
        help_text='Выберите рецепт'
    )
    amount = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name='Количество продукта',
        help_text='Введите количество продукта'
    )

    class Meta:

        verbose_name = 'Продукты в рецепте'
        verbose_name_plural = 'Продукты в рецепте'
        constraints = [
            models.UniqueConstraint(fields=['ingredient', 'recipe'],
                                    name='unique_ingredientrecipe')
        ]

    def __str__(self):

        return f'{self.ingredient} {self.recipe}'
