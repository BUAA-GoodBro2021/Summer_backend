from django.urls import re_path
from utils import consumers

websocket_urlpatterns = [
    re_path(r'room/(?P<group>\w+)/$', consumers.Consumer.as_asgi()),
]
