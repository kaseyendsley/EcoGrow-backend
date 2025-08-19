from rest_framework import serializers
from core.models import Category, Icon, Difficulty, Tag, Quest, UserQuest
from decimal import Decimal
from django.contrib.auth import get_user_model
User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name")


class IconSerializer(serializers.ModelSerializer):
    class Meta:
        model = Icon
        fields = ("id", "name", "icon_url")


class DifficultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Difficulty
        fields = ("id", "name")


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name")


class QuestSerializer(serializers.ModelSerializer):
    # Read-friendly nested objects for GETs
    category = CategorySerializer(read_only=True)
    icon = IconSerializer(read_only=True)
    difficulty = DifficultySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    # Write fields for POST/PUT/PATCH using *_id + tag ids
    category_id = serializers.PrimaryKeyRelatedField(
        source="category", queryset=Category.objects.all(), write_only=True
    )
    icon_id = serializers.PrimaryKeyRelatedField(
        source="icon", queryset=Icon.objects.all(), write_only=True
    )
    difficulty_id = serializers.PrimaryKeyRelatedField(
        source="difficulty", queryset=Difficulty.objects.all(), write_only=True
    )
    tag_ids = serializers.PrimaryKeyRelatedField(
        source="tags", many=True, queryset=Tag.objects.all(), write_only=True, required=False
    )

    class Meta:
        model = Quest
        fields = (
            "id",
            "title",
            "description",
            "is_custom",
            "category", "icon", "difficulty", "tags",
            "category_id", "icon_id", "difficulty_id", "tag_ids",
            "created_by",
        )
        read_only_fields = ("created_by",)

    def create(self, validated_data):
        tags = validated_data.pop("tags", [])
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            validated_data["created_by"] = request.user
        quest = Quest.objects.create(**validated_data)
        if tags:
            quest.tags.set(tags)
        return quest

    def update(self, instance, validated_data):
        tags = validated_data.pop("tags", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tags is not None:
            instance.tags.set(tags)
        return instance


def validate_half_star(value: Decimal) -> Decimal:
    # allow 1.0 .. 5.0 in 0.5 steps
    try:
        d = Decimal(value)
    except Exception:
        raise serializers.ValidationError("Rating must be a number like 3, 4.5, etc.")
    if d < Decimal("1.0") or d > Decimal("5.0"):
        raise serializers.ValidationError("Rating must be between 1 and 5.")
    if (d * 2) % 1 != 0:
        raise serializers.ValidationError("Rating must be in 0.5 increments.")
    return d


class UserQuestSerializer(serializers.ModelSerializer):
    quest = QuestSerializer(read_only=True)
    quest_id = serializers.PrimaryKeyRelatedField(
        source="quest", queryset=Quest.objects.all(), write_only=True
    )
    # Expose stored file path/URL from ImageField (read-only)
    photo = serializers.ImageField(read_only=True)

    class Meta:
        model = UserQuest
        fields = (
            "id",
            "quest", "quest_id",
            "completed", "completed_at",
            "reflection", "rating",
            "photo",  # read-only output of uploaded image
        )
        read_only_fields = ("completed", "completed_at")

    def validate_rating(self, value):
        # Only validate if provided (rating required at completion, not at create)
        if value is None:
            return value
        return validate_half_star(value)


class CompleteUserQuestSerializer(serializers.ModelSerializer):
    """
    Completion requires reflection, rating, and an uploaded photo file.
    No external links allowed.
    """
    rating = serializers.DecimalField(max_digits=2, decimal_places=1)
    photo = serializers.ImageField(required=True)  # upload-only requirement

    class Meta:
        model = UserQuest
        fields = ("reflection", "rating", "photo", "completed_at")

    def validate_rating(self, value):
        return validate_half_star(value)

    def validate_reflection(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Reflection is required.")
        return value

class PublicUserProfileSerializer(serializers.ModelSerializer):
    """
    Public view of a user profile (no email).
    """
    quests_created_count = serializers.SerializerMethodField()
    user_quests_completed_count = serializers.SerializerMethodField()

    class Meta:
        model = User  # resolved via get_user_model()
        fields = (
            "id",
            "username",
            "profile_img",
            "quests_created_count",
            "user_quests_completed_count",
        )

    def get_quests_created_count(self, obj):
        return Quest.objects.filter(created_by=obj).count()

    def get_user_quests_completed_count(self, obj):
        return UserQuest.objects.filter(user=obj, completed=True).count()


class OwnUserProfileSerializer(PublicUserProfileSerializer):
    """
    Private view for the current user (includes email).
    """
    class Meta(PublicUserProfileSerializer.Meta):
        fields = PublicUserProfileSerializer.Meta.fields + ("email",)
