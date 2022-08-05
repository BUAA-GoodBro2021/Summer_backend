from django.urls import path

from . import views

urlpatterns = [
    path('create_token', views.create_token),
    path('parse_token', views.parse_token),
    path('rename_diagram', views.rename_diagram),
    path('delete_diagram', views.delete_diagram),
    path('list_diagram', views.list_diagram),
    path('update_diagram', views.update_diagram),
    path('get_content', views.get_content)
]
