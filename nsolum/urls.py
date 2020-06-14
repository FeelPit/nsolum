"""nsolum URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from nsolum import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('welcome_page/', views.welcome_page),
    path('registration/', views.registration),
    path('login/', views.login),
    path('test/', views.test),
    path('spheres/', views.spheres),
    path('spheres/znakomstva', views.znakomstva),
    path(r'api/<int:idha>/<int:from_years>/<int:to_years>/<int:pp>', views.api_search_meets),
    path(r'api/<int:from_years>/<int:to_years>/<int:rad>', views.api_test),
    path(r'api/user_id', views.api_user_id)
]
