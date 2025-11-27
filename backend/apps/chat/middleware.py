"""
WebSocket authentication middleware for Django Channels.
"""
import logging
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from urllib.parse import parse_qs

logger = logging.getLogger(__name__)


class WebSocketAuthMiddleware:
    """
    Custom middleware for WebSocket authentication.
    Extracts user info from query params or token.
    """
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        query_string = scope.get('query_string', b'').decode()
        query_params = parse_qs(query_string)
        
        user_id = query_params.get('user_id', ['anonymous'])[0]
        user_name = query_params.get('user_name', ['Anonymous'])[0]
        user_email = query_params.get('user_email', [''])[0]
        
        scope['user_id'] = user_id
        scope['user_name'] = user_name
        scope['user_email'] = user_email
        scope['user'] = AnonymousUser()
        
        return await self.app(scope, receive, send)


def WebSocketAuthMiddlewareStack(inner):
    """
    Wrapper for the authentication middleware.
    """
    return WebSocketAuthMiddleware(inner)
