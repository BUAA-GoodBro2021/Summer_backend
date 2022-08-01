from django.urls import path

from . import views

urlpatterns = [
    path('add_team', views.add_team),

]
