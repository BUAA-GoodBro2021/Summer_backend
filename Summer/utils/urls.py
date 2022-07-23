from django.urls import path

from . import views

urlpatterns = [
    # 激活接口
    path('email/<str:token>', views.active),
    # 测试接口
    path('test_login_checker', views.test_login_checker),
    path('test_celery', views.test_celery),
]
