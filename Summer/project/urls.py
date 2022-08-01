from django.urls import path

from . import views

urlpatterns = [
    path('create_project', views.create_project),

]
