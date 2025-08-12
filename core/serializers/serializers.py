from rest_framework import serializers
from core.models import Category, Icon, Difficulty, Tag, Quest


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
