from django.urls import path

from . import views

urlpatterns = [
    path('add_team', views.add_team),
    path('list_team_user', views.list_team_user),
]
