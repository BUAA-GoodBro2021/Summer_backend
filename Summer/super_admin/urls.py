from django.urls import path

from . import views

urlpatterns = [
    # 查询接口
    path('query', views.query),
    # 清空所有缓存
    path('clean_cache', views.clean_cache),
]