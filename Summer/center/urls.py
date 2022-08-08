from django.urls import path

from . import views

urlpatterns = [
    path('list_team_document', views.list_team_document),

]
