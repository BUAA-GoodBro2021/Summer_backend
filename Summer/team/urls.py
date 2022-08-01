from django.urls import path

from . import views

urlpatterns = [
    path('create_team', views.create_team),
    path('list_team_user', views.list_team_user),
    path('list_team_project', views.list_team_project),
    path('invite_user', views.invite_user),
    path('join_team', views.join_team),
    path('set_super_admin', views.set_super_admin),
    path('remove_user', views.remove_user),


]
