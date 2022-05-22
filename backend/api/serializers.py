from rest_framework import serializers
from django.shortcuts import get_object_or_404
from .converters import Base64ImageField
from recipes.models import (
    AmountIngredientForRecipe, Favorite,
    Ingredient, Recipe, ShoppingCart, Tag)
from users.serializers import UserSerializer


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class AmountIngredientForRecipeGetSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True
    )
    id = serializers.IntegerField(source='ingredient.id', read_only=True)

    class Meta:
        model = AmountIngredientForRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class AmountIngredientForRecipePostSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = AmountIngredientForRecipe
        fields = ('id', 'amount')


class RecipeGetSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField(
        method_name='get_ingredients'
    )
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited',
        read_only=True
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart',
        read_only=True
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_ingredients(self, recipe):
        return AmountIngredientForRecipeGetSerializer(
            AmountIngredientForRecipe.objects.filter(recipe=recipe),
            many=True
        ).data

    def get_is_favorited(self, recipe):
        if self.context.get('request').user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=self.context.get('request').user,
            recipe=recipe
        ).exists()

    def get_is_in_shopping_cart(self, recipe):
        if self.context.get('request').user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=self.context.get('request').user,
            recipe=recipe
        ).exists()

    def to_representation(self, obj):
        data = super().to_representation(obj)
        data["image"] = obj.image.url
        return data


class RecipePostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = AmountIngredientForRecipePostSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'ingredients', 'tags',
                  'image', 'name', 'text', 'cooking_time')

    @staticmethod
    def create_ingredients_tags(self, instance, validated_data):
        ingredients, tags = (
            validated_data.get('ingredients'), validated_data.get('tags')
        )
        for ingredient in ingredients:
            count, _ = AmountIngredientForRecipe.objects.get_or_create(
                ingredient=get_object_or_404(Ingredient, pk=ingredient['id']),
                amount=ingredient['amount'],
            )
            instance.ingredients.add(count)
        for tag in tags:
            instance.tags.add(tag)
        return instance

    def create(self, validated_data):
        saved = {}
        saved['ingredients'] = validated_data.pop('ingredients')
        saved['tags'] = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context.get('request').user,
            **validated_data)
        return self.create_ingredients_tags(recipe, saved, validated_data)

    def update(self, instance, validated_data):
        instance.ingredients.clear()
        instance.tags.clear()
        instance = self.create_ingredients_tags(instance, validated_data)
        return super().update(instance, validated_data)

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        ingredients_list = []
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            if ingredient_id in ingredients_list:
                raise serializers.ValidationError({
                    'ingredient': 'Повторяются ингредиенты!'
                })
            ingredients_list.append(ingredient_id)
        return data

    def to_representation(self, obj):
        data = super().to_representation(obj)
        data["image"] = obj.image.url
        return data


class FavoriteRecipesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        if Favorite.objects.filter(
                user=self.context.get('request').user,
                recipe=data['recipe']
        ).exists():
            raise serializers.ValidationError({
                'status': 'Уже добавлен'
            })
        return data

    def to_representation(self, instance):
        return RecipeViewSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data


class RecipeViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def validate(self, data):
        if ShoppingCart.objects.filter(
                user=self.context['request'].user,
                recipe=data['recipe']
        ):
            raise serializers.ValidationError('Уже добавлен')
        return data

    def to_representation(self, instance):
        return RecipeViewSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data
