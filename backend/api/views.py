from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action

from rest_framework.permissions import IsAuthenticated


from .filters import IngredientFilter, RecipeFilter
from .paginator import PagePagination
from .permissions import OwnerOrAdminOrSafeMethods
from .serializers import (FavoriteRecipesSerializer, IngredientSerializer,
                          RecipeGetSerializer, RecipePostSerializer,
                          ShoppingCartSerializer, TagSerializer)
from recipes.models import (
    AmountIngredientForRecipe, Favorite,
    Ingredient, Recipe, ShoppingCart, Tag)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all().order_by('name')
    serializer_class = IngredientSerializer
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all().order_by('id')
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by('-id')
    permission_classes = (OwnerOrAdminOrSafeMethods,)
    pagination_class = PagePagination
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeGetSerializer
        return RecipePostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["POST"],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        return self.post_method_for_actions(
            request=request, pk=pk, serializers=FavoriteRecipesSerializer)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return self.delete_method_for_actions(
            request=request, pk=pk, model=Favorite)

    @action(
        detail=True,
        methods=['POST'],
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        return self.post_method_for_actions(
            request=request, pk=pk, serializers=ShoppingCartSerializer)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        return self.delete_method_for_actions(
            request=request, pk=pk, model=ShoppingCart)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request, pk=None):
        ingredients = AmountIngredientForRecipe.objects.filter(
            recipe__user_shopping_cart__user=request.user.id
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        shopping_cart = ['Список покупок:\n--------------']
        for position, ingredient in enumerate(ingredients, start=1):
            shopping_cart.append(
                f'\n{position}. {ingredient["ingredient__name"]}:'
                f' {ingredient["amount"]}'
                f'({ingredient["ingredient__measurement_unit"]})'
            )
        response = HttpResponse(shopping_cart, content_type='text')
        response['Content-Disposition'] = (
            'attachment;filename=shopping_cart.pdf'
        )
        return response
