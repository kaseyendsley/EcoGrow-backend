from django.db import models

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    profile_img = models.URLField(blank=True, null=True)
    is_moderator = models.BooleanField(default=False)
