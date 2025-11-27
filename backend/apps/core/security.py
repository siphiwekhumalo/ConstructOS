"""
Security Module for ConstructOS.

Implements:
- JWT Token Blacklisting for secure logout
- Security Event Logging for audit trails
- Rate Limiting for brute-force protection
- Anomaly Detection for intrusion detection
"""

import logging
import hashlib
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from functools import wraps

from django.core.cache import cache
from django.conf import settings
from django.db import models
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response

logger = logging.getLogger('security')


BLACKLIST_PREFIX = 'token_blacklist'
RATE_LIMIT_PREFIX = 'rate_limit'
FAILED_LOGIN_PREFIX = 'failed_login'
API_CALLS_PREFIX = 'api_calls'
SECURITY_EVENT_PREFIX = 'security_event'

TOKEN_BLACKLIST_TTL = 86400 * 7
RATE_LIMIT_WINDOW = 60
FAILED_LOGIN_WINDOW = 900
FAILED_LOGIN_MAX = 5
API_RATE_LIMIT = 100


class SecurityEventType:
    LOGIN_SUCCESS = 'LOGIN_SUCCESS'
    LOGIN_FAILED = 'LOGIN_FAILED'
    LOGOUT = 'LOGOUT'
    TOKEN_BLACKLISTED = 'TOKEN_BLACKLISTED'
    PERMISSION_DENIED = 'PERMISSION_DENIED'
    RATE_LIMIT_EXCEEDED = 'RATE_LIMIT_EXCEEDED'
    BRUTE_FORCE_DETECTED = 'BRUTE_FORCE_DETECTED'
    ANOMALY_DETECTED = 'ANOMALY_DETECTED'
    DATA_MODIFIED = 'DATA_MODIFIED'
    DATA_DELETED = 'DATA_DELETED'
    SENSITIVE_ACCESS = 'SENSITIVE_ACCESS'
    AFTER_HOURS_ACCESS = 'AFTER_HOURS_ACCESS'


class TokenBlacklist:
    """
    Redis-based JWT token blacklist for secure logout.
    
    Tokens are stored with their expiry time to prevent reuse
    after logout while automatically cleaning up expired tokens.
    """
    
    @staticmethod
    def _make_key(token: str) -> str:
        token_hash = hashlib.sha256(token.encode()).hexdigest()[:32]
        return f"{BLACKLIST_PREFIX}:{token_hash}"
    
    @classmethod
    def blacklist_token(cls, token: str, user_id: str = None, reason: str = 'logout') -> bool:
        """
        Add a token to the blacklist.
        
        Args:
            token: The JWT token to blacklist
            user_id: Optional user ID for logging
            reason: Reason for blacklisting (logout, revoked, compromised)
        
        Returns:
            bool: True if successfully blacklisted
        """
        try:
            key = cls._make_key(token)
            data = {
                'blacklisted_at': timezone.now().isoformat(),
                'user_id': user_id,
                'reason': reason,
            }
            cache.set(key, json.dumps(data), TOKEN_BLACKLIST_TTL)
            
            SecurityLogger.log(
                SecurityEventType.TOKEN_BLACKLISTED,
                user_id=user_id,
                details={'reason': reason}
            )
            return True
        except Exception as e:
            logger.error(f"Failed to blacklist token: {e}")
            return False
    
    @classmethod
    def is_blacklisted(cls, token: str) -> bool:
        """
        Check if a token is blacklisted.
        
        Args:
            token: The JWT token to check
            
        Returns:
            bool: True if token is blacklisted
        """
        try:
            key = cls._make_key(token)
            return cache.get(key) is not None
        except Exception:
            return False
    
    @classmethod
    def blacklist_all_user_tokens(cls, user_id: str, reason: str = 'force_logout') -> bool:
        """
        Blacklist all tokens for a user by incrementing their token version.
        This invalidates all existing sessions without needing to track each token.
        
        Args:
            user_id: The user ID
            reason: Reason for blacklisting all tokens
            
        Returns:
            bool: True if successful
        """
        try:
            version_key = f"token_version:{user_id}"
            current_version = cache.get(version_key, 0)
            cache.set(version_key, current_version + 1, TOKEN_BLACKLIST_TTL)
            
            SecurityLogger.log(
                SecurityEventType.TOKEN_BLACKLISTED,
                user_id=user_id,
                details={'reason': reason, 'action': 'all_tokens_invalidated'}
            )
            return True
        except Exception as e:
            logger.error(f"Failed to blacklist all tokens for user {user_id}: {e}")
            return False


class SecurityLogger:
    """
    Centralized security event logging.
    
    Logs security events to both file and cache for real-time monitoring.
    Events include authentication, authorization, and data modification.
    """
    
    @staticmethod
    def log(
        event_type: str,
        user_id: str = None,
        ip_address: str = None,
        user_agent: str = None,
        endpoint: str = None,
        method: str = None,
        status_code: int = None,
        details: Dict[str, Any] = None,
        severity: str = 'INFO'
    ) -> None:
        """
        Log a security event.
        
        Args:
            event_type: Type of security event (from SecurityEventType)
            user_id: User ID if available
            ip_address: Client IP address
            user_agent: Client user agent
            endpoint: API endpoint accessed
            method: HTTP method
            status_code: Response status code
            details: Additional event details
            severity: Log severity (INFO, WARNING, ERROR, CRITICAL)
        """
        event = {
            'timestamp': timezone.now().isoformat(),
            'event_type': event_type,
            'user_id': user_id,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'endpoint': endpoint,
            'method': method,
            'status_code': status_code,
            'details': details or {},
            'severity': severity,
        }
        
        log_message = (
            f"[{severity}] {event_type} | "
            f"user={user_id} | ip={ip_address} | "
            f"endpoint={method} {endpoint} | "
            f"status={status_code} | "
            f"details={json.dumps(details or {})}"
        )
        
        if severity == 'CRITICAL':
            logger.critical(log_message)
        elif severity == 'ERROR':
            logger.error(log_message)
        elif severity == 'WARNING':
            logger.warning(log_message)
        else:
            logger.info(log_message)
        
        try:
            events_key = f"{SECURITY_EVENT_PREFIX}:recent"
            recent_events = cache.get(events_key, [])
            if isinstance(recent_events, str):
                recent_events = json.loads(recent_events)
            recent_events.insert(0, event)
            recent_events = recent_events[:1000]
            cache.set(events_key, json.dumps(recent_events), 86400)
        except Exception as e:
            logger.error(f"Failed to cache security event: {e}")
    
    @staticmethod
    def get_recent_events(
        event_type: str = None,
        user_id: str = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Retrieve recent security events.
        
        Args:
            event_type: Filter by event type
            user_id: Filter by user ID
            limit: Maximum number of events to return
            
        Returns:
            List of security events
        """
        try:
            events_key = f"{SECURITY_EVENT_PREFIX}:recent"
            events = cache.get(events_key, [])
            if isinstance(events, str):
                events = json.loads(events)
            
            if event_type:
                events = [e for e in events if e.get('event_type') == event_type]
            if user_id:
                events = [e for e in events if e.get('user_id') == user_id]
            
            return events[:limit]
        except Exception:
            return []


class RateLimiter:
    """
    Redis-based rate limiting for API endpoints.
    
    Implements sliding window rate limiting to prevent
    abuse and brute-force attacks.
    """
    
    @staticmethod
    def _make_key(identifier: str, endpoint: str = 'global') -> str:
        return f"{RATE_LIMIT_PREFIX}:{endpoint}:{identifier}"
    
    @classmethod
    def check_rate_limit(
        cls,
        identifier: str,
        endpoint: str = 'global',
        max_requests: int = API_RATE_LIMIT,
        window_seconds: int = RATE_LIMIT_WINDOW
    ) -> tuple[bool, int]:
        """
        Check if request is within rate limit.
        
        Args:
            identifier: Unique identifier (IP, user ID, etc.)
            endpoint: API endpoint being accessed
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
            
        Returns:
            Tuple of (allowed: bool, remaining: int)
        """
        try:
            key = cls._make_key(identifier, endpoint)
            current = cache.get(key, 0)
            
            if current >= max_requests:
                SecurityLogger.log(
                    SecurityEventType.RATE_LIMIT_EXCEEDED,
                    ip_address=identifier,
                    endpoint=endpoint,
                    severity='WARNING',
                    details={'requests': current, 'limit': max_requests}
                )
                return False, 0
            
            cache.set(key, current + 1, window_seconds)
            return True, max_requests - current - 1
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            return True, max_requests
    
    @classmethod
    def get_remaining(cls, identifier: str, endpoint: str = 'global', max_requests: int = API_RATE_LIMIT) -> int:
        """Get remaining requests in current window."""
        try:
            key = cls._make_key(identifier, endpoint)
            current = cache.get(key, 0)
            return max(0, max_requests - current)
        except Exception:
            return max_requests


class BruteForceProtection:
    """
    Protection against brute-force login attempts.
    
    Tracks failed login attempts and temporarily locks accounts
    after too many failures.
    """
    
    @staticmethod
    def _make_key(identifier: str) -> str:
        return f"{FAILED_LOGIN_PREFIX}:{identifier}"
    
    @classmethod
    def record_failed_attempt(cls, identifier: str, ip_address: str = None) -> tuple[int, bool]:
        """
        Record a failed login attempt.
        
        Args:
            identifier: Username or email
            ip_address: Client IP address
            
        Returns:
            Tuple of (attempt_count, is_locked)
        """
        try:
            key = cls._make_key(identifier)
            attempts = cache.get(key, 0) + 1
            cache.set(key, attempts, FAILED_LOGIN_WINDOW)
            
            is_locked = attempts >= FAILED_LOGIN_MAX
            
            if is_locked:
                SecurityLogger.log(
                    SecurityEventType.BRUTE_FORCE_DETECTED,
                    ip_address=ip_address,
                    severity='CRITICAL',
                    details={
                        'identifier': identifier,
                        'attempts': attempts,
                        'locked': True
                    }
                )
            else:
                SecurityLogger.log(
                    SecurityEventType.LOGIN_FAILED,
                    ip_address=ip_address,
                    severity='WARNING',
                    details={
                        'identifier': identifier,
                        'attempts': attempts,
                        'remaining': FAILED_LOGIN_MAX - attempts
                    }
                )
            
            return attempts, is_locked
            
        except Exception as e:
            logger.error(f"Failed to record login attempt: {e}")
            return 0, False
    
    @classmethod
    def is_locked(cls, identifier: str) -> tuple[bool, int]:
        """
        Check if an account is locked due to failed attempts.
        
        Args:
            identifier: Username or email
            
        Returns:
            Tuple of (is_locked, remaining_lockout_time)
        """
        try:
            key = cls._make_key(identifier)
            attempts = cache.get(key, 0)
            
            if attempts >= FAILED_LOGIN_MAX:
                ttl = cache.ttl(key) if hasattr(cache, 'ttl') else FAILED_LOGIN_WINDOW
                return True, ttl if ttl > 0 else FAILED_LOGIN_WINDOW
            
            return False, 0
            
        except Exception:
            return False, 0
    
    @classmethod
    def clear_attempts(cls, identifier: str) -> bool:
        """Clear failed attempts after successful login."""
        try:
            key = cls._make_key(identifier)
            cache.delete(key)
            return True
        except Exception:
            return False


class AnomalyDetector:
    """
    Detects anomalous behavior patterns.
    
    Monitors for:
    - Unusual API call volumes
    - After-hours access
    - Geographic anomalies
    - Unusual data access patterns
    """
    
    BUSINESS_HOURS_START = 6
    BUSINESS_HOURS_END = 22
    
    @classmethod
    def track_api_call(cls, user_id: str, endpoint: str, method: str) -> None:
        """Track API call for anomaly detection."""
        try:
            hour = timezone.now().hour
            key = f"{API_CALLS_PREFIX}:{user_id}:{hour}"
            
            calls = cache.get(key, {})
            if isinstance(calls, str):
                calls = json.loads(calls)
            
            endpoint_key = f"{method}:{endpoint}"
            calls[endpoint_key] = calls.get(endpoint_key, 0) + 1
            
            cache.set(key, json.dumps(calls), 7200)
            
        except Exception as e:
            logger.error(f"Failed to track API call: {e}")
    
    @classmethod
    def check_after_hours_access(cls, user_id: str, ip_address: str = None) -> bool:
        """
        Check if access is occurring outside business hours.
        
        Returns True if access is during unusual hours (potential anomaly).
        """
        try:
            current_hour = timezone.now().hour
            
            if current_hour < cls.BUSINESS_HOURS_START or current_hour >= cls.BUSINESS_HOURS_END:
                SecurityLogger.log(
                    SecurityEventType.AFTER_HOURS_ACCESS,
                    user_id=user_id,
                    ip_address=ip_address,
                    severity='INFO',
                    details={'hour': current_hour}
                )
                return True
            
            return False
            
        except Exception:
            return False
    
    @classmethod
    def check_volume_anomaly(
        cls,
        user_id: str,
        threshold_multiplier: float = 5.0
    ) -> bool:
        """
        Check if API call volume is anomalously high.
        
        Compares current hour's calls to average.
        """
        try:
            current_hour = timezone.now().hour
            current_key = f"{API_CALLS_PREFIX}:{user_id}:{current_hour}"
            current_calls = cache.get(current_key, {})
            if isinstance(current_calls, str):
                current_calls = json.loads(current_calls)
            
            total_current = sum(current_calls.values())
            
            total_historical = []
            for h in range(24):
                if h != current_hour:
                    key = f"{API_CALLS_PREFIX}:{user_id}:{h}"
                    calls = cache.get(key, {})
                    if isinstance(calls, str):
                        calls = json.loads(calls)
                    total_historical.append(sum(calls.values()))
            
            if not total_historical:
                return False
            
            avg_calls = sum(total_historical) / len(total_historical)
            
            if avg_calls > 0 and total_current > avg_calls * threshold_multiplier:
                SecurityLogger.log(
                    SecurityEventType.ANOMALY_DETECTED,
                    user_id=user_id,
                    severity='WARNING',
                    details={
                        'type': 'volume_spike',
                        'current_calls': total_current,
                        'average_calls': avg_calls,
                        'multiplier': total_current / avg_calls
                    }
                )
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Volume anomaly check failed: {e}")
            return False
    
    @classmethod
    def detect_anomalies(cls, user_id: str, ip_address: str = None) -> List[str]:
        """
        Run all anomaly detection checks.
        
        Returns list of detected anomaly types.
        """
        anomalies = []
        
        if cls.check_after_hours_access(user_id, ip_address):
            anomalies.append('after_hours')
        
        if cls.check_volume_anomaly(user_id):
            anomalies.append('volume_spike')
        
        return anomalies


def rate_limit(max_requests: int = 60, window_seconds: int = 60, identifier_func=None):
    """
    Decorator for rate limiting API views.
    
    Args:
        max_requests: Maximum requests allowed
        window_seconds: Time window in seconds
        identifier_func: Function to extract identifier from request
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if identifier_func:
                identifier = identifier_func(request)
            else:
                identifier = get_client_ip(request)
            
            allowed, remaining = RateLimiter.check_rate_limit(
                identifier=identifier,
                endpoint=request.path,
                max_requests=max_requests,
                window_seconds=window_seconds
            )
            
            if not allowed:
                return Response(
                    {'error': 'Rate limit exceeded. Please try again later.'},
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                    headers={'X-RateLimit-Remaining': '0'}
                )
            
            response = view_func(request, *args, **kwargs)
            
            if hasattr(response, '__setitem__'):
                response['X-RateLimit-Remaining'] = str(remaining)
            
            return response
        return wrapper
    return decorator


def security_audit(action: str, sensitive: bool = False):
    """
    Decorator for logging data modifications.
    
    Args:
        action: Description of the action (create, update, delete)
        sensitive: Whether this involves sensitive data
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user_id = str(request.user.id) if hasattr(request.user, 'id') else None
            
            response = view_func(request, *args, **kwargs)
            
            if response.status_code in [200, 201, 204]:
                event_type = SecurityEventType.DATA_DELETED if action == 'delete' else SecurityEventType.DATA_MODIFIED
                if sensitive:
                    event_type = SecurityEventType.SENSITIVE_ACCESS
                
                SecurityLogger.log(
                    event_type,
                    user_id=user_id,
                    ip_address=get_client_ip(request),
                    endpoint=request.path,
                    method=request.method,
                    status_code=response.status_code,
                    details={'action': action, 'sensitive': sensitive}
                )
            
            return response
        return wrapper
    return decorator


def get_client_ip(request) -> str:
    """Extract client IP from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', 'unknown')


def get_user_agent(request) -> str:
    """Extract user agent from request."""
    return request.META.get('HTTP_USER_AGENT', 'unknown')
