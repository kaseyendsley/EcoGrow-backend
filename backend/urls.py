from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter
from core.status import health
from core.views.auth_views import RegisterView
from core.views.me_views import MeView
from core.views.logout_views import LogoutView
from core.views.quest_views import QuestViewSet
from core.views.user_quest_views import UserQuestViewSet 
from core.views.catalog_views import CategoryViewSet, TagViewSet, DifficultyViewSet, IconViewSet 
from core.views.user_views import UserProfileViewSet
from core.views.subscription_views import SubscriptionViewSet 
from core.views.feed import FeedView


from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r"quests", QuestViewSet, basename="quest")
router.register(r"user-quests", UserQuestViewSet, basename="userquest")
router.register(r"categories", CategoryViewSet, basename="category")     
router.register(r"tags", TagViewSet, basename="tag")                    
router.register(r"difficulties", DifficultyViewSet, basename="difficulty") 
router.register(r"icons", IconViewSet, basename="icon")  
router.register(r"users", UserProfileViewSet, basename="user")
router.register(r"subscriptions", SubscriptionViewSet, basename="subscription")



urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health),
    path("api/auth/login/", obtain_auth_token),
    path("api/auth/register/", RegisterView.as_view()), 
    path("api/auth/me/", MeView.as_view()),
    path("api/auth/logout/", LogoutView.as_view()),
    path("api/", include(router.urls)),
    path("api/feed/", FeedView.as_view(), name="feed"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)