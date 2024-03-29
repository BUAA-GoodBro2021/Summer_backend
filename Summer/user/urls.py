from django.urls import path

from . import views

urlpatterns = [
    path('register', views.register),
    path('login', views.login),
    path('find_password', views.find_password),
    path('upload_avatar', views.upload_avatar),
    path('list_team', views.list_team),
    path('list_star', views.list_star),
]
