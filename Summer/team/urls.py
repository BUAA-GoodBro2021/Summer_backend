from django.urls import path

from . import views

urlpatterns = [
    path('create_team', views.create_team),
    path('list_team_user', views.list_team_user),
    path('invite_user', views.invite_user),
    path('join_team', views.join_team),
]
