from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    User personalizzato esteso - Requisito del progetto
    """
    email = models.EmailField(unique=True)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Statistiche user
    polls_created = models.IntegerField(default=0)
    votes_cast = models.IntegerField(default=0)

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'custom_user'