from django.urls import path

from . import views

urlpatterns = [
    path('list_project_page', views.list_project_page),
]