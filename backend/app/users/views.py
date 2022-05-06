from djoser.views import UserViewSet
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_list_or_404, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.pagination import (
    LimitOffsetPagination, PageNumberPagination,
)
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from app import settings

from .serializers import UserSerializer, RegistrationSerializer
from users.models import User 




class UserViewSet(UserViewSet):
    """Api viewset for work with user model."""
    queryset = User.objects.all()
    serializer_class = RegistrationSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @action(
        methods=["patch", "get"],
        permission_classes=[IsAuthenticated],
        detail=False,
        url_path="me",
        url_name="me",
    )
    def me(self, request, *args, **kwargs):
        user = self.request.user
        serializer = UserSerializer(user)
        if self.request.method == "PATCH" and user.role != "user":
            serializer = UserSerializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(serializer.data)

