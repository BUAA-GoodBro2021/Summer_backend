from django.urls import path

from . import views

urlpatterns = [
    path('list_document_user', views.list_document_user),
    path('rename_document', views.rename_document),
    path('delete_document', views.delete_document),
    path('save_document', views.save_document),
    path('edit_document', views.edit_document),
    path('parse_token', views.parse_token),
    path('create_token', views.create_token),
    path('list_document', views.list_document),
]
