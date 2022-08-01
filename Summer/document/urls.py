from django.urls import path

from . import views

urlpatterns = [
    path('example', views.example),
    path('create_document', views.create_document),
    path('list_document_user', views.list_document_user),
    path('delete_document', views.delete_document),
]
