# core/views/user_views.py
from django.contrib.auth import get_user_model
from rest_framework import viewsets, status, serializers
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import Quest, UserQuest
from core.serializers.serializers import (
    PublicUserProfileSerializer,
    OwnUserProfileSerializer,
    QuestSerializer,
    UserQuestSerializer,
)

User = get_user_model()


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Minimal update serializer for the current user.
    Only allows username/email changes.
    """
    class Meta:
        model = User
        fields = ("username", "email")
        extra_kwargs = {
            "username": {"required": False},
            "email": {"required": False},
        }


class UserProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    - GET     /api/users/<id>/                       -> public profile (no email)
    - GET     /api/users/me/                         -> own profile (includes email)
    - PATCH   /api/users/me/                         -> update own username/email
    - DELETE  /api/users/me/                         -> delete own account
    - GET     /api/users/<id>/created-quests/        -> quests this user created
    - GET     /api/users/<id>/completed-user-quests/ -> this user's completed UserQuests
    """
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = PublicUserProfileSerializer

    @action(detail=False, methods=["get", "patch", "delete"], permission_classes=[IsAuthenticated])
    def me(self, request):
        method = request.method.lower()

        if method == "get":
            ser = OwnUserProfileSerializer(request.user, context={"request": request})
            return Response(ser.data)

        if method == "patch":
            upd = UserProfileUpdateSerializer(
                instance=request.user,
                data=request.data,
                partial=True,
                context={"request": request},
            )
            upd.is_valid(raise_exception=True)
            upd.save()
            out = OwnUserProfileSerializer(request.user, context={"request": request})
            return Response(out.data, status=status.HTTP_200_OK)

        # DELETE
        request.user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["get"], url_path="created-quests")
    def created_quests(self, request, pk=None):
        """
        List quests created by this user.
        Public endpoint.
        """
        user = self.get_object()
        qs = (
            Quest.objects.filter(created_by=user)
            .select_related("category", "icon", "difficulty")
            .prefetch_related("tags")
            .order_by("-id")
        )
        page = self.paginate_queryset(qs)
        ser = QuestSerializer(page or qs, many=True, context={"request": request})
        if page is not None:
            return self.get_paginated_response(ser.data)
        return Response(ser.data)

    @action(detail=True, methods=["get"], url_path="completed-user-quests")
    def completed_user_quests(self, request, pk=None):
        """
        List completed UserQuests for this user (includes reflection, rating, photo, etc.).
        Public endpoint.
        """
        user = self.get_object()
        qs = (
            UserQuest.objects.filter(user=user, completed=True)
            .select_related(
                "quest",
                "quest__category",
                "quest__icon",
                "quest__difficulty",
            )
            .prefetch_related("quest__tags")
            .order_by("-completed_at", "-id")
        )
        page = self.paginate_queryset(qs)
        ser = UserQuestSerializer(page or qs, many=True, context={"request": request})
        if page is not None:
            return self.get_paginated_response(ser.data)
        return Response(ser.data)
