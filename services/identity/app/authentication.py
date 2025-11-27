"""
Azure AD JWT Authentication for Identity Service.
"""
import os
import jwt
import requests
from datetime import datetime, timedelta
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import User


class AzureJWTAuthentication(BaseAuthentication):
    """
    JWT authentication using Azure AD tokens.
    Validates tokens and creates/updates users as needed.
    """
    
    _jwks_cache = None
    _jwks_cache_time = None
    _cache_duration = timedelta(hours=24)
    
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header[7:]
        
        try:
            payload = self._validate_token(token)
            user = self._get_or_create_user(payload)
            return (user, token)
        except Exception as e:
            raise AuthenticationFailed(f'Token validation failed: {str(e)}')
    
    def _validate_token(self, token):
        """Validate JWT token against Azure AD."""
        tenant_id = getattr(settings, 'AZURE_AD_TENANT_ID', '')
        client_id = getattr(settings, 'AZURE_AD_CLIENT_ID', '')
        
        if not tenant_id or not client_id:
            unverified = jwt.decode(token, options={"verify_signature": False})
            return unverified
        
        signing_key = self._get_signing_key(token, tenant_id)
        
        payload = jwt.decode(
            token,
            signing_key,
            algorithms=['RS256'],
            audience=client_id,
            issuer=f'https://login.microsoftonline.com/{tenant_id}/v2.0',
        )
        
        return payload
    
    def _get_signing_key(self, token, tenant_id):
        """Get signing key from Azure AD JWKS endpoint."""
        if self._should_refresh_jwks():
            self._refresh_jwks(tenant_id)
        
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get('kid')
        
        for key in self._jwks_cache.get('keys', []):
            if key.get('kid') == kid:
                return jwt.algorithms.RSAAlgorithm.from_jwk(key)
        
        raise AuthenticationFailed('Unable to find signing key')
    
    def _should_refresh_jwks(self):
        if self._jwks_cache is None:
            return True
        if self._jwks_cache_time is None:
            return True
        return datetime.utcnow() - self._jwks_cache_time > self._cache_duration
    
    def _refresh_jwks(self, tenant_id):
        jwks_url = f'https://login.microsoftonline.com/{tenant_id}/discovery/v2.0/keys'
        response = requests.get(jwks_url)
        response.raise_for_status()
        AzureJWTAuthentication._jwks_cache = response.json()
        AzureJWTAuthentication._jwks_cache_time = datetime.utcnow()
    
    def _get_or_create_user(self, payload):
        """Get or create user from JWT payload."""
        azure_oid = payload.get('oid')
        email = payload.get('preferred_username') or payload.get('email', '')
        name = payload.get('name', '')
        roles = payload.get('roles', [])
        
        name_parts = name.split(' ', 1) if name else ['', '']
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        user = None
        if azure_oid:
            user = User.objects.filter(azure_ad_object_id=azure_oid).first()
        
        if not user and email:
            user = User.objects.filter(email=email).first()
        
        if not user:
            username = email.split('@')[0] if email else f'user_{azure_oid[:8]}'
            user = User.objects.create(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                azure_ad_object_id=azure_oid,
                azure_ad_roles=roles,
            )
        else:
            user.azure_ad_object_id = azure_oid
            user.azure_ad_roles = roles
            if first_name:
                user.first_name = first_name
            if last_name:
                user.last_name = last_name
            user.save()
        
        return user
