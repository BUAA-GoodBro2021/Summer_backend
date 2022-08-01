from django.urls import path

from . import views

urlpatterns = [
    path('create_project', views.create_project),
    path('rename_project', views.rename_project),
]