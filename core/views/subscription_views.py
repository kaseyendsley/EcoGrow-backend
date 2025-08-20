# core/views/subscription_views.py
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from rest_framework import serializers, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import Subscription

User = get_user_model()


class TargetUserLiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username")


class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Minimal serializer for follow/subscription.
    - follower is implied from request.user (read-only in output)
    - target_id is write-only PK for creating a follow
    - target is a tiny nested shape for display
    """
    target_id = serializers.PrimaryKeyRelatedField(
        source="target",
        queryset=User.objects.all(),
        write_only=True,
    )
    target = TargetUserLiteSerializer(read_only=True)

    class Meta:
        model = Subscription
        fields = ("id", "created_at", "target_id", "target")
        read_only_fields = ("id", "created_at")

    def create(self, validated_data):
        request = self.context.get("request")
        follower = getattr(request, "user", None)
        if not follower or not follower.is_authenticated:
            raise serializers.ValidationError({"detail": "Authentication required."})

        target = validated_data["target"]
        if follower == target:
            raise serializers.ValidationError({"detail": "You cannot subscribe to yourself."})

        try:
            sub = Subscription.objects.create(follower=follower, target=target)
        except IntegrityError:
            # unique_subscription violated -> already following
            raise serializers.ValidationError({"detail": "Already subscribed to this user."})
        return sub


class SubscriptionViewSet(viewsets.ModelViewSet):
    """
    Routes (to be registered via router):
      - GET    /api/subscriptions/           -> list users I follow (targets)
      - POST   /api/subscriptions/           -> follow (body: { "target_id": <user_pk> })
      - DELETE /api/subscriptions/{id}/      -> unfollow
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        # Only show the current user's subscriptions; include target user
        return (
            Subscription.objects
            .select_related("target")
            .filter(follower=self.request.user)
            .order_by("-created_at")
        )

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        sub = ser.save()
        out = self.get_serializer(sub)
        return Response(out.data, status=status.HTTP_201_CREATED)
