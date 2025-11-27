"""
ASGI config for ConstructOS project.

Exposes the ASGI callable as a module-level variable named ``application``.
Supports both HTTP and WebSocket protocols via Django Channels.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

from backend.apps.chat.middleware import WebSocketAuthMiddlewareStack
from backend.apps.chat.routing import websocket_urlpatterns

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        WebSocketAuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
})
