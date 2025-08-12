from django.db import models

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class User(AbstractUser):
    profile_img = models.URLField(blank=True, null=True)
    is_moderator = models.BooleanField(default=False)


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Icon(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon_url = models.URLField()

    def __str__(self):
        return self.name


class Difficulty(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=80, unique=True)

    def __str__(self):
        return self.name


class Quest(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    difficulty = models.ForeignKey(Difficulty, on_delete=models.PROTECT, related_name="quests")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="quests")
    icon = models.ForeignKey(Icon, on_delete=models.PROTECT, related_name="quests")
    is_custom = models.BooleanField(default=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_quests")
    tags = models.ManyToManyField(Tag, related_name="quests", blank=True)

    def __str__(self):
        return self.title
