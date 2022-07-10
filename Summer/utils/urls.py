from django.urls import path

from . import views

urlpatterns = [
    path('email/<str:token>', views.active),
    path('test_login_checker', views.test_login_checker),
    path('test_redis_cache', views.test_redis_cache),
]
