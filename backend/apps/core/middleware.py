"""
Security middleware for ConstructOS.

Provides:
- Input sanitization and XSS prevention
- Request/response logging for security audit
- API tracking for anomaly detection
"""

import re
import html
import json
import logging
from typing import Any, Dict, Optional

from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

from .security import (
    SecurityLogger,
    SecurityEventType,
    AnomalyDetector,
    get_client_ip,
    get_user_agent,
)

logger = logging.getLogger('security.middleware')


DANGEROUS_PATTERNS = [
    re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL),
    re.compile(r'javascript:', re.IGNORECASE),
    re.compile(r'on\w+\s*=', re.IGNORECASE),
    re.compile(r'<iframe[^>]*>', re.IGNORECASE),
    re.compile(r'<object[^>]*>', re.IGNORECASE),
    re.compile(r'<embed[^>]*>', re.IGNORECASE),
    re.compile(r'expression\s*\(', re.IGNORECASE),
    re.compile(r'url\s*\(\s*[\'"]?\s*data:', re.IGNORECASE),
]

SQL_INJECTION_PATTERNS = [
    re.compile(r'\b(union|select|insert|update|delete|drop|alter|create)\b.*\b(from|into|table|database)\b', re.IGNORECASE),
    re.compile(r';\s*(drop|delete|update|insert)\b', re.IGNORECASE),
    re.compile(r'--\s*$', re.MULTILINE),
    re.compile(r'/\*.*\*/', re.DOTALL),
]


def sanitize_string(value: str) -> str:
    """
    Sanitize a string value to prevent XSS attacks.
    HTML-encodes dangerous characters.
    """
    if not isinstance(value, str):
        return value
    
    return html.escape(value, quote=True)


def check_dangerous_patterns(value: str) -> bool:
    """
    Check if a string contains dangerous patterns.
    Returns True if dangerous content is detected.
    """
    if not isinstance(value, str):
        return False
    
    for pattern in DANGEROUS_PATTERNS:
        if pattern.search(value):
            return True
    
    for pattern in SQL_INJECTION_PATTERNS:
        if pattern.search(value):
            return True
    
    return False


def sanitize_dict(data: Dict[str, Any], check_only: bool = False) -> tuple[Dict[str, Any], bool]:
    """
    Recursively sanitize a dictionary.
    
    Args:
        data: Dictionary to sanitize
        check_only: If True, only check for dangerous content without modifying
        
    Returns:
        Tuple of (sanitized_dict, has_dangerous_content)
    """
    has_dangerous = False
    sanitized = {}
    
    for key, value in data.items():
        if isinstance(value, str):
            if check_dangerous_patterns(value):
                has_dangerous = True
                if check_only:
                    return data, True
            sanitized[key] = sanitize_string(value) if not check_only else value
        elif isinstance(value, dict):
            sanitized_value, nested_dangerous = sanitize_dict(value, check_only)
            sanitized[key] = sanitized_value
            has_dangerous = has_dangerous or nested_dangerous
        elif isinstance(value, list):
            sanitized_list = []
            for item in value:
                if isinstance(item, str):
                    if check_dangerous_patterns(item):
                        has_dangerous = True
                    sanitized_list.append(sanitize_string(item) if not check_only else item)
                elif isinstance(item, dict):
                    sanitized_item, nested_dangerous = sanitize_dict(item, check_only)
                    sanitized_list.append(sanitized_item)
                    has_dangerous = has_dangerous or nested_dangerous
                else:
                    sanitized_list.append(item)
            sanitized[key] = sanitized_list
        else:
            sanitized[key] = value
    
    return sanitized, has_dangerous


class SecurityMiddleware(MiddlewareMixin):
    """
    Security middleware that provides:
    - XSS detection and prevention
    - SQL injection detection
    - Request logging for audit
    - Anomaly tracking
    """
    
    SKIP_PATHS = [
        '/api/v1/health/',
        '/api/v1/cache/stats/',
        '/static/',
        '/favicon.ico',
    ]
    
    SENSITIVE_PATHS = [
        '/api/v1/auth/',
        '/api/v1/security/',
        '/api/v1/users/',
    ]
    
    def should_skip(self, path: str) -> bool:
        """Check if path should skip security checks."""
        for skip_path in self.SKIP_PATHS:
            if path.startswith(skip_path):
                return True
        return False
    
    def is_sensitive_path(self, path: str) -> bool:
        """Check if path is security-sensitive."""
        for sensitive_path in self.SENSITIVE_PATHS:
            if path.startswith(sensitive_path):
                return True
        return False
    
    def process_request(self, request):
        """
        Process incoming request for security threats.
        
        Note: Avoids reading request.body to prevent breaking DRF parsers.
        Body validation is delegated to InputValidationMiddleware and views.
        """
        if self.should_skip(request.path):
            return None
        
        ip_address = get_client_ip(request)
        
        for key, value in request.GET.items():
            if check_dangerous_patterns(value):
                SecurityLogger.log(
                    SecurityEventType.ANOMALY_DETECTED,
                    ip_address=ip_address,
                    user_agent=get_user_agent(request),
                    endpoint=request.path,
                    method=request.method,
                    details={
                        'type': 'dangerous_query_param',
                        'param': key,
                    },
                    severity='WARNING'
                )
                break
        
        user_id = request.session.get('user_id')
        if user_id:
            AnomalyDetector.track_api_call(user_id, request.path, request.method)
        
        return None
    
    def process_response(self, request, response):
        """
        Process response and add security headers.
        """
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        if request.is_secure():
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        if hasattr(response, 'status_code'):
            if response.status_code == 403:
                user_id = request.session.get('user_id')
                SecurityLogger.log(
                    SecurityEventType.PERMISSION_DENIED,
                    user_id=user_id,
                    ip_address=get_client_ip(request),
                    user_agent=get_user_agent(request),
                    endpoint=request.path,
                    method=request.method,
                    status_code=403,
                    severity='WARNING'
                )
        
        return response


class InputValidationMiddleware(MiddlewareMixin):
    """
    Middleware for validating input data.
    
    Note: This middleware only validates but does not modify request data
    to avoid breaking DRF parsers. Sanitization should happen at the
    serializer/view level.
    """
    
    MAX_FIELD_LENGTH = 10000
    MAX_BODY_SIZE = 10 * 1024 * 1024
    
    EXEMPT_PATHS = [
        '/api/v1/documents/upload/',
        '/admin/',
        '/api/v1/health/',
        '/static/',
    ]
    
    def should_exempt(self, path: str) -> bool:
        """Check if path should be exempt from validation."""
        for exempt_path in self.EXEMPT_PATHS:
            if path.startswith(exempt_path):
                return True
        return False
    
    def process_request(self, request):
        """Validate request input without modifying the request body."""
        if self.should_exempt(request.path):
            return None
        
        for key, value in request.GET.items():
            if isinstance(value, str):
                if len(value) > self.MAX_FIELD_LENGTH:
                    return JsonResponse(
                        {'error': f'Query parameter "{key}" exceeds maximum length'},
                        status=400
                    )
                if check_dangerous_patterns(value):
                    ip_address = get_client_ip(request)
                    SecurityLogger.log(
                        SecurityEventType.ANOMALY_DETECTED,
                        ip_address=ip_address,
                        endpoint=request.path,
                        method=request.method,
                        details={'type': 'dangerous_query_param', 'param': key},
                        severity='WARNING'
                    )
        
        return None
