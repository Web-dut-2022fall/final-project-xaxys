"""
WSGI config for chat project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chat.settings")

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from core import routing as core_routing

application = ProtocolTypeRouter({
    "websocket": AuthMiddlewareStack(URLRouter(core_routing.websocket_urlpatterns)),
    "http": get_asgi_application(),
})