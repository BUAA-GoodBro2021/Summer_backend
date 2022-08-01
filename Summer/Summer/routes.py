from django.urls import re_path
from utils import consumers

websocket_urlpatterns = [
    re_path(r'websocket/(?P<document_id>\w+)/$', consumers.Consumer.as_asgi()),
]
