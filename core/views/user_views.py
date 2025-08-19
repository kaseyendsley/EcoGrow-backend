# core/views/user_views.py
from django.contrib.auth import get_user_model
from rest_framework import viewsets, status, serializers
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from core.serializers.serializers import (
    PublicUserProfileSerializer,
    OwnUserProfileSerializer,
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
    - GET    /api/users/<id>/   -> public profile (no email)
    - GET    /api/users/me/     -> own profile (includes email)
    - PATCH  /api/users/me/     -> update own username/email
    - DELETE /api/users/me/     -> delete own account
    """
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = PublicUserProfileSerializer

    @action(detail=False, methods=["get", "patch", "delete"], permission_classes=[IsAuthenticated])
    def me(self, request):
        if request.method.lower() == "get":
            ser = OwnUserProfileSerializer(request.user, context={"request": request})
            return Response(ser.data)

        if request.method.lower() == "patch":
            upd = UserProfileUpdateSerializer(
                instance=request.user,
                data=request.data,
                partial=True,
                context={"request": request},
            )
            upd.is_valid(raise_exception=True)
            upd.save()
            # return the full "own" profile shape
            out = OwnUserProfileSerializer(request.user, context={"request": request})
            return Response(out.data, status=status.HTTP_200_OK)

        # DELETE
        request.user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
