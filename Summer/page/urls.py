from django.urls import path

from . import views

urlpatterns = [
    path('create', views.create_page),
    path('all', views.list_project_all),
    path('detail', views.list_page_detail),
    path('edit/request', views.edit_request),
    path('edit/save', views.edit_save),
    path('img', views.upload_img),
]
