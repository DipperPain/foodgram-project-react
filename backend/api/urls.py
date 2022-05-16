from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import TagViewSet, RecipeViewSet, IngredientViewSet
from users import views


router = DefaultRouter()
router.register(r'tags', TagViewSet)
router.register(r'recipes', RecipeViewSet)
router.register(r'ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('users/subscriptions/',
         views.SubscribeViewSet.as_view({'get': 'list'}),
         name='subscriptions'),
    path('users/<users_id>/subscribe/',
         views.SubscribeViewSet.as_view(
          {'post': 'create', 'delete': 'delete'}), name='subscribe'),
    path('', include(router.urls)),
]
