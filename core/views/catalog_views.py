# core/views/catalog_views.py
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from core.models import Category, Tag, Difficulty, Icon
from core.serializers.serializers import (
    CategorySerializer, TagSerializer, DifficultySerializer, IconSerializer
)

class PublicReadOnly(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]

class CategoryViewSet(PublicReadOnly):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer

class TagViewSet(PublicReadOnly):
    queryset = Tag.objects.all().order_by("name")
    serializer_class = TagSerializer

class DifficultyViewSet(PublicReadOnly):
    queryset = Difficulty.objects.all().order_by("name")
    serializer_class = DifficultySerializer

class IconViewSet(PublicReadOnly):
    queryset = Icon.objects.all().order_by("name")
    serializer_class = IconSerializer
