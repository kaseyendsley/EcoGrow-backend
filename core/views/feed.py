from itertools import chain

from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# Models
from core.models import Quest, UserQuest, Subscription

User = get_user_model()


def _serialize_activity_item(item):
    """
    item dict keys:
      - type: "quest_created" | "userquest_completed"
      - ts: datetime
      - user: User instance (creator/completer)
      - quest: Quest instance or None
      - userquest: UserQuest instance or None
    """
    # ✅ Import directly from the submodule (your real file)
    from core.serializers.serializers import QuestSerializer, UserQuestSerializer

    ts = item["ts"].isoformat().replace("+00:00", "Z") if item["ts"] else None
    user = item["user"]

    payload = {
        "type": item["type"],
        "ts": ts,
        "user": {
            "id": user.id,
            "username": user.username,
            "profile_img": getattr(user, "profile_img", None),
        },
    }

    if item["type"] == "quest_created" and item["quest"] is not None:
        payload["quest"] = QuestSerializer(item["quest"]).data

    if item["type"] == "userquest_completed" and item["userquest"] is not None:
        payload["user_quest"] = UserQuestSerializer(item["userquest"]).data

    return payload


class FeedView(APIView):
    """
    GET /api/feed/?scope=all|subscribed&limit=20&offset=0
    Returns newest-first mixed activity:
      - quest_created (from Quest.created_at)
      - userquest_completed (from UserQuest.completed_at)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        scope = (request.query_params.get("scope") or "subscribed").lower()
        try:
            limit = int(request.query_params.get("limit", 20))
        except ValueError:
            limit = 20
        try:
            offset = int(request.query_params.get("offset", 0))
        except ValueError:
            offset = 0

        # Subscriptions
        subscribed_user_ids = None
        if scope == "subscribed":
            # 🔧 FIX: your model uses `follower` (who follows) and `target` (who is followed)
            subscribed_user_ids = list(
                Subscription.objects.filter(follower=request.user)
                .values_list("target_id", flat=True)
            )
            if not subscribed_user_ids:
                return Response({"results": [], "count": 0})

        # Quests (quest_created)
        quests_qs = (
            Quest.objects
            .select_related("created_by")
            .only("id", "created_by_id", "created_at")
        )
        if scope == "subscribed":
            quests_qs = quests_qs.filter(created_by_id__in=subscribed_user_ids)

        # UserQuests (userquest_completed)
        userquests_qs = (
            UserQuest.objects
            .select_related("user", "quest", "quest__created_by")
            .filter(~Q(completed_at=None))
            .only("id", "user_id", "quest_id", "completed_at")
        )
        if scope == "subscribed":
            userquests_qs = userquests_qs.filter(user_id__in=subscribed_user_ids)

        # Normalize + sort
        quest_items = [
            {
                "type": "quest_created",
                "ts": q.created_at,
                "user": getattr(q, "created_by", None),
                "quest": q,
                "userquest": None,
            }
            for q in quests_qs
            if getattr(q, "created_by", None) is not None
        ]

        userquest_items = [
            {
                "type": "userquest_completed",
                "ts": uq.completed_at,
                "user": uq.user,
                "quest": uq.quest,
                "userquest": uq,
            }
            for uq in userquests_qs
        ]

        items = list(chain(quest_items, userquest_items))
        items.sort(key=lambda x: (x["ts"] is not None, x["ts"]), reverse=True)

        count = len(items)
        window = items[offset : offset + limit]

        data = [_serialize_activity_item(itm) for itm in window]
        return Response({"results": data, "count": count})
