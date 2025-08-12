from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from core.models import Quest
from core.serializers.serializers import QuestSerializer
from core.permissions import IsOwnerOrReadOnly


class QuestViewSet(viewsets.ModelViewSet):
    queryset = (
        Quest.objects
        .select_related("category", "icon", "difficulty", "created_by")
        .prefetch_related("tags")
        .all()
        .order_by("id")
    )
    serializer_class = QuestSerializer
    permission_classes = [IsOwnerOrReadOnly]

    # ensures serializer has request to set created_by on create()
    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx

    # DELETE safety net (optional; permission checks already handle it)
    def perform_destroy(self, instance):
        user = self.request.user
        if not (user.is_staff or instance.created_by_id == user.id):
            raise PermissionDenied("Only the creator or staff can delete this quest.")
        instance.delete()
