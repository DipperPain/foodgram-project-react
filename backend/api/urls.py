from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import TagViewSet, RecipeViewSet, IngredientViewSet
from users import views


router_1 = DefaultRouter()
router_1.register(r'tags', TagViewSet)
router_1.register(r'recipes', RecipeViewSet)
router_1.register(r'ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('users/subscriptions/',
         views.SubscribeViewSet.as_view({'get': 'list'}),
         name='subscriptions'),
    path('users/<users_id>/subscribe/',
         views.SubscribeViewSet.as_view(
          {'post': 'create', 'delete': 'delete'}), name='subscribe'),
    path('', include(router_1.urls)),
]
