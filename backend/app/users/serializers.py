from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from django.db.models import Avg, IntegerField
from rest_framework import exceptions, serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from users.models import User
from recipes.models import (Cart, Favorite, Ingredient,
                            Recipe, Subscribe, Tag)

from app.settings import (
    MESSAGE_FOR_RESERVED_NAME, MESSAGE_FOR_USER_NOT_FOUND, RESERVED_NAME,
)


class MyAuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField(label=_("Email"))
    password = serializers.CharField(
        label=_("Password",),
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                email=email, password=password)

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class CommonSubscribed(metaclass=serializers.SerializerMetaclass):
    """
    Class for check subscribed on user.
    """
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        """
        Function for check arg=='is_subsubscribed'.
        """
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        if Subscribe.objects.filter(
                user=request.user, following__id=obj.id).exists():
            return True
        else:
            return False

class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = (
            'email',
            'first_name',
            'last_name',
            'role',
        )
        read_only_fields = ('role',)

    def validate_username(self, value):
        if value == RESERVED_NAME:
            raise serializers.ValidationError(MESSAGE_FOR_RESERVED_NAME)
        return value


class UserEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    def create(self, validated_data):
        return User.objects.create(**validated_data)


class RegistrationSerializer(UserCreateSerializer, CommonSubscribed):
    """
    Создание сериализатора модели пользователя.
    """
    class Meta:
        """
        Мета параметры сериализатора модели пользователя.
        """
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'username',
                  'last_name', 'is_subscribed', 'password')
        write_only_fields = ('password',)
        read_only_fields = ('id',)
        extra_kwargs = {'is_subscribed': {'required': False}}

