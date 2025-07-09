from django.contrib.auth.models import AbstractUser
from django.db import models

from core.constatns import (
    MAX_USER_NAME_LENGTH, MAX_EMAIL_LENGTH
)


class CustomUser(AbstractUser):
    email = models.EmailField(
        'email',
        unique=True,
        max_length=MAX_EMAIL_LENGTH,
    )
    first_name = models.CharField(
        'first name', max_length=MAX_USER_NAME_LENGTH
    )
    last_name = models.CharField(
        'last name', max_length=MAX_USER_NAME_LENGTH
    )
    avatar = models.ImageField(
        'avatar', upload_to='users/avatars/',
        blank=True, null=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username', 'first_name',
        'last_name', 'password'
    ]

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __str__(self):
        return self.email


class Subscription(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        unique_together = ('user', 'author')
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
