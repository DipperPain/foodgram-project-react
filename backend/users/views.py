from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import RegistrationSerializer, UserSerializer
from users.models import User


class UserViewSet(UserViewSet):
    """Api viewset for work with user model."""
    serializer_class = RegistrationSerializer

    def get_queryset(self):
        return User.objects.all()

    @action(
        methods=['patch', 'get'],
        permission_classes=[IsAuthenticated],
        detail=False,
        url_path='me',
        url_name='me',
    )
    def me(self, request, *args, **kwargs):
        user = self.request.user
        serializer = UserSerializer(user)
        if self.request.method == 'PATCH' and user.role != 'user':
            serializer = UserSerializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(serializer.data)
