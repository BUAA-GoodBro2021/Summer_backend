from django.urls import re_path
from utils import consumers

websocket_urlpatterns = [
    re_path(r'wss/(?P<page_id>.+)/(?P<user>.+)/$', consumers.Consumer.as_asgi()),
]
