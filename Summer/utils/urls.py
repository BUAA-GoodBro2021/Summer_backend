from django.urls import path

from . import views

urlpatterns = [
    path('email/<str:token>', views.active),
    path('test', views.test_login_checker),
]
