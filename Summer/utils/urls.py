from django.urls import path

from . import views

urlpatterns = [
    # 激活接口
    path('email/<str:token>', views.active),
    # 测试接口
    path('test_celery', views.test_celery),
    path('clear_redis', views.clear_redis),
    path('set_redis', views.set_redis),
    path('clear_redis_all', views.clear_redis_all),

]
