from django.urls import path

from . import views

urlpatterns = [
    path('register', views.register),
    path('login', views.login),
    path('find_password', views.find_password),
    path('upload_avatar', views.upload_avatar),
]
