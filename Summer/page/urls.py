from django.urls import path

from . import views

urlpatterns = [
    path('example', views.example),
    path('create', views.create_page),
    path('all', views.list_project_all),
    path('detail', views.list_page_detail),
    path('edit/save', views.edit_save),
    path('img', views.upload_img),
    path('delete', views.delete_page),
    path('get_current', views.get_current),
    path('change_preview', views.change_preview),
    path('preview/all', views.list_preview_all),
    path('preview/detail', views.list_preview_detail),
    path('add_material', views.add_material),
    path('delete_material', views.delete_material),
    path('get_material_list', views.get_material_list),
    path('add_model', views.add_model),
    path('delete_model', views.delete_model),
    path('get_model_list', views.get_model_list),
]
