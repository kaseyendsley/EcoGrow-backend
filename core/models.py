# from django.db import models

# from django.contrib.auth.models import AbstractUser
# from django.db import models
# from django.conf import settings
# from django.db.models import Q
# from django.db.models.signals import pre_save, post_delete
# from django.dispatch import receiver


# class User(AbstractUser):
#     profile_img = models.URLField(blank=True, null=True)
#     is_moderator = models.BooleanField(default=False)


# class Category(models.Model):
#     name = models.CharField(max_length=100, unique=True)

#     def __str__(self):
#         return self.name


# class Icon(models.Model):
#     name = models.CharField(max_length=100, unique=True)
#     icon_url = models.URLField()

#     def __str__(self):
#         return self.name


# class Difficulty(models.Model):
#     name = models.CharField(max_length=50, unique=True)

#     def __str__(self):
#         return self.name


# class Tag(models.Model):
#     name = models.CharField(max_length=80, unique=True)

#     def __str__(self):
#         return self.name


# class Quest(models.Model):
#     title = models.CharField(max_length=200)
#     description = models.TextField(blank=True)
#     difficulty = models.ForeignKey(Difficulty, on_delete=models.PROTECT, related_name="quests")
#     category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="quests")
#     icon = models.ForeignKey(Icon, on_delete=models.PROTECT, related_name="quests")
#     is_custom = models.BooleanField(default=False)
#     created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="created_quests", null=True,
#         blank=True)
#     tags = models.ManyToManyField(Tag, related_name="quests", blank=True)

#     def __str__(self):
#         return self.title
    

# class UserQuest(models.Model):
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="user_quests",
#     )
#     quest = models.ForeignKey(
#         "core.Quest",
#         on_delete=models.CASCADE,
#         related_name="user_quests",
#     )
#     photo = models.ImageField(upload_to="user_quests/%Y/%m/%d/", blank=True, null=True)

#     # progress
#     completed = models.BooleanField(default=False)
#     completed_at = models.DateTimeField(null=True, blank=True)

#     # completion data
#     reflection = models.TextField(blank=True)  # required on completion; optional before
#     photo_url = models.URLField(blank=True)    # optional
#     # 1–5 in 0.5 steps; kept nullable until completion
#     rating = models.DecimalField(max_digits=2, decimal_places=1, null=True, blank=True)

#     class Meta:
#         # allow repeats after completion, but only ONE active at a time
#         constraints = [
#             models.UniqueConstraint(
#                 fields=["user", "quest"],
#                 condition=Q(completed=False),
#                 name="unique_active_user_quest_per_user_and_quest",
#             )
#         ]

#     def __str__(self):
#         status = "completed" if self.completed else "in-progress"
#         return f"UserQuest(user={self.user_id}, quest={self.quest_id}, {status})"

# # --- File cleanup helpers ---

# @receiver(pre_save, sender=UserQuest)
# def delete_old_photo_on_change(sender, instance, **kwargs):
#     """
#     If a new photo is uploaded, delete the previous file from storage.
#     """
#     if not instance.pk:
#         return
#     try:
#         old = sender.objects.get(pk=instance.pk)
#     except sender.DoesNotExist:
#         return
#     old_file = getattr(old, "photo", None)
#     new_file = getattr(instance, "photo", None)
#     if old_file and old_file.name and old_file != new_file:
#         if old_file.storage.exists(old_file.name):
#             old_file.storage.delete(old_file.name)

# @receiver(post_delete, sender=UserQuest)
# def delete_photo_on_delete(sender, instance, **kwargs):
#     """
#     When a UserQuest is deleted, also remove its photo file.
#     """
#     f = getattr(instance, "photo", None)
#     if f and f.name and f.storage.exists(f.name):
#         f.storage.delete(f.name)

# core/models.py
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models
from django.db.models import Q, F
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver


class User(AbstractUser):
    profile_img = models.URLField(blank=True, null=True)
    is_moderator = models.BooleanField(default=False)

    def __str__(self):
        return self.username


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
    difficulty = models.ForeignKey(
        Difficulty, on_delete=models.PROTECT, related_name="quests"
    )
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="quests"
    )
    icon = models.ForeignKey(Icon, on_delete=models.PROTECT, related_name="quests")
    is_custom = models.BooleanField(default=False)

    # IMPORTANT: do not cascade Quest on user delete; we keep quests around
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_quests",
    )

    tags = models.ManyToManyField(Tag, related_name="quests", blank=True)

    def __str__(self):
        return self.title


class UserQuest(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_quests",
    )
    quest = models.ForeignKey(
        "core.Quest",
        on_delete=models.CASCADE,
        related_name="user_quests",
    )
    # uploaded proof photo (served via MEDIA_URL)
    photo = models.ImageField(upload_to="user_quests/%Y/%m/%d/", blank=True, null=True)

    # progress
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    # completion data
    reflection = models.TextField(blank=True)  # required on completion; optional before
    photo_url = models.URLField(blank=True)    # legacy/unused by new flow; safe to keep
    rating = models.DecimalField(max_digits=2, decimal_places=1, null=True, blank=True)

    class Meta:
        # allow repeats after completion, but only ONE active at a time
        constraints = [
            models.UniqueConstraint(
                fields=["user", "quest"],
                condition=Q(completed=False),
                name="unique_active_user_quest_per_user_and_quest",
            )
        ]

    def __str__(self):
        status = "completed" if self.completed else "in-progress"
        return f"UserQuest(user={self.user_id}, quest={self.quest_id}, {status})"


# --- NEW: Subscriptions (follow relationship) ---

class Subscription(models.Model):
    """
    A user (follower) subscribes to another user (target).
    - Unique per (follower, target)
    - Cannot follow yourself (DB-level check)
    """
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="following",
    )
    target = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="followers",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["follower", "target"],
                name="unique_subscription",
            ),
            models.CheckConstraint(
                check=~Q(follower=F("target")),
                name="no_self_follow",
            ),
        ]

    def __str__(self):
        return f"{self.follower_id} -> {self.target_id}"


# --- File cleanup helpers (UserQuest photo files) ---

@receiver(pre_save, sender=UserQuest)
def delete_old_photo_on_change(sender, instance, **kwargs):
    """
    If a new photo is uploaded, delete the previous file from storage.
    """
    if not instance.pk:
        return
    try:
        old = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return
    old_file = getattr(old, "photo", None)
    new_file = getattr(instance, "photo", None)
    if old_file and old_file.name and old_file != new_file:
        if old_file.storage.exists(old_file.name):
            old_file.storage.delete(old_file.name)


@receiver(post_delete, sender=UserQuest)
def delete_photo_on_delete(sender, instance, **kwargs):
    """
    When a UserQuest is deleted, also remove its photo file.
    """
    f = getattr(instance, "photo", None)
    if f and f.name and f.storage.exists(f.name):
        f.storage.delete(f.name)
