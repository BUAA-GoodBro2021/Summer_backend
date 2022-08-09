from django.urls import path

from . import views

urlpatterns = [
    path('example', views.example),
    path('create', views.create_page),
    path('all', views.list_project_all),
    path('detail', views.list_page_detail),
    # path('edit/request', views.edit_request),
    path('edit/save', views.edit_save),
    path('img', views.upload_img),
    path('delete', views.delete_page),
    path('get_current', views.get_current),
    path('change_preview', views.change_preview),
]
