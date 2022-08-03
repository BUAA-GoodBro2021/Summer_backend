from django.urls import path

from . import views

urlpatterns = [
    path('create_diagram', views.create_diagram),
    path('create_token', views.create_token),
    path('parse_token', views.parse_token),
]
