from djoser.views import UserViewSet
from .serializers import RegistrationSerializer
from users.models import User


class UserViewSet(UserViewSet):
    """Api viewset for work with user model."""
    serializer_class = RegistrationSerializer

    def get_queryset(self):
        return User.objects.all()
