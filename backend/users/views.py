from djoser.views import UserViewSet
from rest_framework.viewsets import ModelViewSet
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import (
    RegistrationSerializer,
    UserSerializer, CommonSubscribed)
from users.models import User, Subscribe


class UserViewSet(UserViewSet):
    """Api viewset for work with user model."""
    serializer_class = RegistrationSerializer

    def get_queryset(self):
        return User.objects.all()


class SubscribeViewSet(ModelViewSet):
    """ Make subscribe."""
    serializer_class = CommonSubscribed
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return get_list_or_404(User, following__user=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Create Subscribe.
        """
        user_id = self.kwargs.get('users_id')
        user = get_object_or_404(User, id=user_id)
        Subscribe.objects.create(
            user=request.user, following=user)
        return Response(status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        """
        Delete Subscribe.
        """
        author_id = self.kwargs['users_id']
        user_id = request.user.id
        subscribe = get_object_or_404(
            Subscribe, user__id=user_id, following__id=author_id)
        subscribe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
