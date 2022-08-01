from django.urls import path

from . import views

urlpatterns = [
    path('create_project', views.create_project),
    path('rename_project', views.rename_project),
    path('remove_project_to_bin', views.remove_project_to_bin),
    path('recover_project_from_bin', views.recover_project_from_bin),
]
