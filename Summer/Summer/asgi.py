"""
ASGI config for Summer project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from . import routes

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Summer.settings')
django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(routes.websocket_urlpatterns)
})
