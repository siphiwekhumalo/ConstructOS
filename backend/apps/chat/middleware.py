"""
WebSocket authentication middleware for Django Channels.
Validates Azure AD JWT tokens for WebSocket connections.
"""
import os
import logging
import jwt
import requests
from datetime import datetime, timezone
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from urllib.parse import parse_qs

logger = logging.getLogger(__name__)

AZURE_AD_TENANT_ID = os.environ.get('AZURE_AD_TENANT_ID', '')
AZURE_AD_CLIENT_ID = os.environ.get('AZURE_AD_CLIENT_ID', '')
AZURE_AD_ISSUER = f'https://login.microsoftonline.com/{AZURE_AD_TENANT_ID}/v2.0'
AZURE_AD_JWKS_URL = f'https://login.microsoftonline.com/{AZURE_AD_TENANT_ID}/discovery/v2.0/keys'

_jwks_cache = None
_jwks_cache_time = None
JWKS_CACHE_DURATION = 3600


def get_jwks():
    """Fetch and cache the JWKS (JSON Web Key Set) from Azure AD."""
    global _jwks_cache, _jwks_cache_time
    
    if _jwks_cache and _jwks_cache_time:
        cache_age = (datetime.now(timezone.utc) - _jwks_cache_time).total_seconds()
        if cache_age < JWKS_CACHE_DURATION:
            return _jwks_cache
    
    try:
        response = requests.get(AZURE_AD_JWKS_URL, timeout=10)
        response.raise_for_status()
        _jwks_cache = response.json()
        _jwks_cache_time = datetime.now(timezone.utc)
        return _jwks_cache
    except requests.RequestException as e:
        logger.error(f"Failed to fetch JWKS: {e}")
        if _jwks_cache:
            return _jwks_cache
        return None


def validate_azure_token(token):
    """
    Validate an Azure AD JWT token and return the decoded claims.
    
    Args:
        token: The JWT token string
        
    Returns:
        dict: The decoded token claims or None if validation fails
    """
    if not AZURE_AD_TENANT_ID or not AZURE_AD_CLIENT_ID:
        logger.debug("Azure AD not configured, skipping token validation")
        return None
    
    try:
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get('kid')
        
        if not kid:
            logger.warning("Token missing key ID (kid)")
            return None
        
        jwks = get_jwks()
        if not jwks:
            logger.error("JWKS unavailable")
            return None
        
        signing_key = None
        for key in jwks.get('keys', []):
            if key.get('kid') == kid:
                signing_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
                break
        
        if not signing_key:
            logger.warning("Unable to find matching key")
            return None
        
        claims = jwt.decode(
            token,
            signing_key,
            algorithms=['RS256'],
            audience=AZURE_AD_CLIENT_ID,
            issuer=AZURE_AD_ISSUER,
            options={
                'verify_exp': True,
                'verify_aud': True,
                'verify_iss': True,
            }
        )
        
        return claims
        
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        return None
    except jwt.InvalidAudienceError:
        logger.warning("Invalid token audience")
        return None
    except jwt.InvalidIssuerError:
        logger.warning("Invalid token issuer")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        return None
    except Exception as e:
        logger.error(f"Token validation error: {e}")
        return None


class AuthenticatedUser:
    """Simple user class for WebSocket authentication context."""
    def __init__(self, user_id, name, email, roles=None):
        self.id = user_id
        self.azure_ad_object_id = user_id
        self.name = name
        self.email = email
        self.username = email
        self.roles = roles or []
        self.is_authenticated = True
        self.is_anonymous = False
    
    def __str__(self):
        return f"AuthenticatedUser({self.email})"


class DemoUser:
    """Demo user for development/testing when Azure AD is not configured."""
    def __init__(self, user_id='demo-user', name='Demo User', email='demo@constructos.co.za'):
        self.id = user_id
        self.azure_ad_object_id = user_id
        self.name = name
        self.email = email
        self.username = email
        self.roles = ['Site_Manager']
        self.is_authenticated = True
        self.is_anonymous = False
    
    def __str__(self):
        return f"DemoUser({self.email})"


class WebSocketAuthMiddleware:
    """
    Secure middleware for WebSocket authentication.
    
    Authentication methods (in order of priority):
    1. Azure AD JWT token in 'token' query parameter
    2. Azure AD JWT token in 'authorization' query parameter
    3. Demo mode (only when AZURE_AD_TENANT_ID is not set)
    
    If Azure AD is configured, a valid token is REQUIRED.
    If Azure AD is not configured, demo mode allows testing.
    """
    
    def __init__(self, app):
        self.app = app
        self.azure_configured = bool(AZURE_AD_TENANT_ID and AZURE_AD_CLIENT_ID)
    
    async def __call__(self, scope, receive, send):
        query_string = scope.get('query_string', b'').decode()
        query_params = parse_qs(query_string)
        
        token = (
            query_params.get('token', [None])[0] or 
            query_params.get('authorization', [None])[0]
        )
        
        user = None
        user_id = None
        user_name = None
        user_email = None
        
        if token:
            claims = validate_azure_token(token)
            
            if claims:
                user_id = claims.get('oid', '')
                user_name = claims.get('name', '')
                user_email = claims.get('email') or claims.get('preferred_username', '')
                roles = claims.get('roles', [])
                
                user = AuthenticatedUser(
                    user_id=user_id,
                    name=user_name,
                    email=user_email,
                    roles=roles
                )
                
                logger.info(f"WebSocket authenticated: {user_email}")
            else:
                logger.warning("Invalid token provided for WebSocket connection")
                
                if self.azure_configured:
                    await send({
                        'type': 'websocket.close',
                        'code': 4001,
                    })
                    return
        
        if not user:
            if self.azure_configured:
                logger.warning("WebSocket connection rejected: no valid token and Azure AD is configured")
                await send({
                    'type': 'websocket.close',
                    'code': 4001,
                })
                return
            else:
                user = DemoUser()
                user_id = user.id
                user_name = user.name
                user_email = user.email
                logger.debug("WebSocket using demo user (Azure AD not configured)")
        
        scope['user'] = user
        scope['user_id'] = user_id or user.id
        scope['user_name'] = user_name or user.name
        scope['user_email'] = user_email or user.email
        
        return await self.app(scope, receive, send)


def WebSocketAuthMiddlewareStack(inner):
    """
    Wrapper for the authentication middleware.
    """
    return WebSocketAuthMiddleware(inner)
