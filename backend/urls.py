"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
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

router = DefaultRouter()
router.register(r"quests", QuestViewSet, basename="quest")
router.register(r"user-quests", UserQuestViewSet, basename="userquest")
router.register(r"categories", CategoryViewSet, basename="category")     
router.register(r"tags", TagViewSet, basename="tag")                    
router.register(r"difficulties", DifficultyViewSet, basename="difficulty") 
router.register(r"icons", IconViewSet, basename="icon")                 


urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health),

    # auth
    path("api/auth/login/", obtain_auth_token),
    path("api/auth/register/", RegisterView.as_view()), 
    path("api/auth/me/", MeView.as_view()),
    path("api/auth/logout/", LogoutView.as_view()),

    # API endpoints from ViewSets
    path("api/", include(router.urls)),
]
