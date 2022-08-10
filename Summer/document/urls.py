from django.urls import path

from . import views

urlpatterns = [
    path('list_document_user', views.list_document_user),
    path('save_document', views.save_document),
    path('edit_document', views.edit_document),
    path('parse_token', views.parse_token),
    path('list_project_tree_document', views.list_project_tree_document),
    path('create_tree_folder', views.create_tree_folder),
    path('create_tree_token', views.create_tree_token),
    path('delete_tree_document', views.delete_tree_document),
    path('rename_tree_document', views.rename_tree_document),
    path('move_tree_document', views.move_tree_document),
    path('list_folder_document', views.list_folder_document),
    path('copy_document', views.copy_document),
    path('copy_folder', views.copy_folder),
]
