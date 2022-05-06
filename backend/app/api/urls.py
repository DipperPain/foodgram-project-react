from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import TagViewSet, RecipeViewSet

router = DefaultRouter()
router.register(r'tags', TagViewSet)
router.register(r'recipes', RecipeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
