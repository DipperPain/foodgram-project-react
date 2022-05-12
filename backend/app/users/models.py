from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy


class User(AbstractUser):
    class Role:
        USER = "user"
        ADMIN = "admin"

        @classmethod
        def cls_choices(self):
            return [
                (getattr(self, k), getattr(self, k))
                for k in self.__dict__.keys()
                if isinstance(getattr(self, k), str) and "_" not in k
            ]

    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(gettext_lazy("email address"), unique=True)
    confirmation_code = models.CharField(max_length=60, blank=True)
    first_name = models.TextField(max_length=300, blank=True)
    last_name = models.TextField(max_length=300, blank=True)
    role = models.CharField(
        max_length=25, choices=Role.choices(), default=Role.USER
    )

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN
