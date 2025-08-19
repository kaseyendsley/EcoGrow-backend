from django.db import IntegrityError
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from core.models import UserQuest
from core.serializers.serializers import (
    UserQuestSerializer,
    CompleteUserQuestSerializer,
)


class UserQuestViewSet(viewsets.ModelViewSet):
    """
    Endpoints:
      - GET /api/user-quests/                (list mine)
      - POST /api/user-quests/               (adopt: requires quest_id)
      - GET /api/user-quests/{id}/           (retrieve mine)
      - PATCH /api/user-quests/{id}/         (edit before completion if desired)
      - DELETE /api/user-quests/{id}/        (cancel/remove)
      - POST /api/user-quests/{id}/complete/ (finish: requires reflection + rating; optional photo FILE + optional completed_at)
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserQuestSerializer

    def get_queryset(self):
        # only the current user's user_quests
        return (
            UserQuest.objects
            .filter(user=self.request.user)
            .select_related(
                "quest",
                "quest__category",
                "quest__icon",
                "quest__difficulty",
            )
            .prefetch_related("quest__tags")
            .order_by("-id")
        )

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx

    def perform_create(self, serializer):
        # Just save; don't return a Response here
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)
        except IntegrityError:
            return Response(
                {"detail": "You already have this quest in progress."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Re-serialize the saved instance so the response has the full object
        out = self.get_serializer(serializer.instance)
        headers = self.get_success_headers(out.data)
        return Response(out.data, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        # allow delete regardless of completion status
        instance = self.get_object()  # already restricted to current user via get_queryset
        return super().destroy(request, *args, **kwargs)

    @action(
        detail=True,
        methods=["post"],
        parser_classes=[MultiPartParser, FormParser, JSONParser],
    )
    def complete(self, request, pk=None):
        uq = self.get_object()
        if uq.completed:
            return Response({"detail": "Already completed."}, status=status.HTTP_400_BAD_REQUEST)

        ser = CompleteUserQuestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        uq.reflection = data["reflection"]
        uq.rating = data["rating"]

        # Optional file upload; replace old file if provided
        new_photo = data.get("photo")
        if new_photo:
            if uq.photo and getattr(uq.photo, "name", ""):
                # delete old file from storage but keep model instance intact
                uq.photo.delete(save=False)
            uq.photo = new_photo

        uq.completed_at = data.get("completed_at") or timezone.now()
        uq.completed = True
        uq.save()

        return Response(self.get_serializer(uq).data, status=status.HTTP_200_OK)
