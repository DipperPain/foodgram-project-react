from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import (
    UserViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet)



urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken'))
]
