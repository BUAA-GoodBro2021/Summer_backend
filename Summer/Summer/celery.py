from celery import Celery
from django.conf import settings
from properties import *
import os

# 启动 celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Summer.settings')

# 创建 celery
app = Celery('Summer')
app.conf.update(
    BROKER_URL='redis://:' + redis_PASSWORD + '@' +
               redis_HOST + '/4',
)

# 配置每个应用的 worker 工作
app.autodiscover_tasks(settings.INSTALLED_APPS)
