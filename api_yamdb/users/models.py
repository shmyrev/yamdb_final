from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone

USER = 'user'
ADMIN = 'admin'
MODERATOR = 'moderator'

ROLES = ((USER, 'Аутентифицированный пользователь'),
         (MODERATOR, 'Модератор'),
         (ADMIN, 'Администратор'))


class User(AbstractUser):
    """Модель прользователей"""
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+$',
            message='Недопустимый символ в имени'
        )]
    )
    email = models.EmailField(
        max_length=254, unique=True, blank=False, null=False
    )
    first_name = models.CharField("имя", max_length=150, blank=True, null=True)
    last_name = models.CharField(
        "фамилия", max_length=150, blank=True, null=True)
    bio = models.TextField('Биография', blank=True, null=True)
    role = models.CharField(
        'Роль пользователя', max_length=15, choices=ROLES, default=USER)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    @property
    def is_user(self):
        return self.role == USER

    @property
    def is_admin(self):
        return self.role == ADMIN

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    class Meta:
        ordering = ('pk',)
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
