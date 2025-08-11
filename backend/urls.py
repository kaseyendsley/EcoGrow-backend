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
from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from core.status import health
from core.views.auth_views import RegisterView 
from core.views.me_views import MeView 
from core.views.logout_views import LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health),
    path("api/auth/login/", obtain_auth_token),
    path("api/auth/register/", RegisterView.as_view()), 
    path("api/auth/me/", MeView.as_view()),
    path("api/auth/logout/", LogoutView.as_view()),
]
