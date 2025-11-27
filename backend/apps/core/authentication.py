"""
Azure AD JWT Authentication Backend for Django REST Framework.

This module provides authentication using Microsoft Entra ID (Azure AD) tokens.
It validates JWT tokens, extracts user information, and syncs users to the database.
"""

import os
import jwt
import requests
import logging
from datetime import datetime, timezone
from django.conf import settings
from rest_framework import authentication, exceptions
from .models import User

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
        raise exceptions.AuthenticationFailed('Unable to validate token: JWKS unavailable')


def get_signing_key(token):
    """Get the signing key from JWKS that matches the token's key ID."""
    try:
        unverified_header = jwt.get_unverified_header(token)
    except jwt.exceptions.DecodeError as e:
        raise exceptions.AuthenticationFailed(f'Invalid token header: {e}')
    
    kid = unverified_header.get('kid')
    if not kid:
        raise exceptions.AuthenticationFailed('Token missing key ID (kid)')
    
    jwks = get_jwks()
    for key in jwks.get('keys', []):
        if key.get('kid') == kid:
            return jwt.algorithms.RSAAlgorithm.from_jwk(key)
    
    raise exceptions.AuthenticationFailed('Unable to find matching key')


def validate_azure_token(token):
    """
    Validate an Azure AD JWT token and return the decoded claims.
    
    Args:
        token: The JWT token string
        
    Returns:
        dict: The decoded token claims
        
    Raises:
        AuthenticationFailed: If the token is invalid
    """
    if not AZURE_AD_TENANT_ID or not AZURE_AD_CLIENT_ID:
        raise exceptions.AuthenticationFailed(
            'Azure AD not configured. Set AZURE_AD_TENANT_ID and AZURE_AD_CLIENT_ID.'
        )
    
    try:
        signing_key = get_signing_key(token)
        
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
        raise exceptions.AuthenticationFailed('Token has expired')
    except jwt.InvalidAudienceError:
        raise exceptions.AuthenticationFailed('Invalid token audience')
    except jwt.InvalidIssuerError:
        raise exceptions.AuthenticationFailed('Invalid token issuer')
    except jwt.InvalidTokenError as e:
        raise exceptions.AuthenticationFailed(f'Invalid token: {e}')


def sync_user_from_token(claims):
    """
    Create or update a user based on Azure AD token claims.
    
    Args:
        claims: Decoded JWT claims from Azure AD
        
    Returns:
        User: The synced user instance
    """
    azure_oid = claims.get('oid')
    email = claims.get('email') or claims.get('preferred_username', '')
    name = claims.get('name', '')
    roles = claims.get('roles', [])
    
    if not azure_oid:
        raise exceptions.AuthenticationFailed('Token missing object ID (oid)')
    
    name_parts = name.split(' ', 1) if name else ['', '']
    first_name = name_parts[0]
    last_name = name_parts[1] if len(name_parts) > 1 else ''
    
    primary_role = 'user'
    role_mapping = {
        'Finance_User': 'finance',
        'HR_Manager': 'hr',
        'Operations_Specialist': 'operations',
        'Site_Manager': 'site_manager',
        'Administrator': 'admin',
        'Executive': 'executive',
    }
    
    for azure_role in roles:
        if azure_role in role_mapping:
            primary_role = role_mapping[azure_role]
            break
    
    try:
        user = User.objects.get(azure_ad_object_id=azure_oid)
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.azure_ad_roles = roles
        user.role = primary_role
        user.last_login = datetime.now(timezone.utc)
        user.save()
        
    except User.DoesNotExist:
        username = email.split('@')[0] if email else azure_oid[:8]
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        
        user = User.objects.create(
            azure_ad_object_id=azure_oid,
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=primary_role,
            azure_ad_roles=roles,
            last_login=datetime.now(timezone.utc),
            is_active=True,
        )
    
    return user


class AzureADAuthentication(authentication.BaseAuthentication):
    """
    Azure AD JWT authentication for Django REST Framework.
    
    Authenticates requests using Bearer tokens issued by Microsoft Entra ID.
    Tokens are validated against the JWKS endpoint and user info is synced.
    """
    
    def authenticate(self, request):
        """
        Authenticate the request and return a (user, token) tuple.
        
        Returns None if authentication was not attempted.
        Raises AuthenticationFailed if authentication fails.
        """
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header:
            return None
        
        parts = auth_header.split()
        
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return None
        
        token = parts[1]
        
        claims = validate_azure_token(token)
        
        user = sync_user_from_token(claims)
        
        if not user.is_active:
            raise exceptions.AuthenticationFailed('User account is disabled')
        
        return (user, claims)
    
    def authenticate_header(self, request):
        """Return the WWW-Authenticate header value for 401 responses."""
        return 'Bearer realm="api"'


class OptionalAzureADAuthentication(AzureADAuthentication):
    """
    Azure AD authentication that allows unauthenticated access.
    
    If a valid token is provided, the user is authenticated.
    If no token is provided, request.user will be None.
    This is useful for endpoints that behave differently for authenticated users.
    """
    
    def authenticate(self, request):
        """Allow requests without authentication."""
        try:
            return super().authenticate(request)
        except exceptions.AuthenticationFailed:
            return None
