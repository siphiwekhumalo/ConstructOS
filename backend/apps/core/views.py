from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.db.models import Q
from .models import User, Event, AuditLog, Favorite
from .serializers import UserSerializer, UserCreateSerializer, EventSerializer, AuditLogSerializer, FavoriteSerializer
from .permissions import IsAuthenticated, IsSystemAdmin, IsFinanceManager, IsHRSpecialist, get_user_permissions
from .security import (
    SecurityLogger, 
    SecurityEventType, 
    RateLimiter, 
    BruteForceProtection,
    AnomalyDetector,
    TokenBlacklist,
)


class AuthMeView(APIView):
    """
    Return the current authenticated user's profile, roles, and permissions.
    Works with both Azure AD auth and session-based auth.
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        user_id = request.session.get('user_id')
        
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                if user.is_active:
                    permissions = get_user_permissions(user)
                    return Response({
                        'user': {
                            'id': str(user.id),
                            'username': user.username,
                            'email': user.email,
                            'first_name': user.first_name,
                            'last_name': user.last_name,
                            'full_name': user.get_full_name(),
                            'role': user.role,
                            'role_display': user.get_role_display(),
                            'user_type': user.user_type,
                            'department': user.department,
                            'is_admin': user.is_admin,
                            'is_executive': user.is_executive,
                            'is_internal': user.is_internal,
                        },
                        'permissions': permissions,
                    })
            except User.DoesNotExist:
                request.session.flush()
        
        user = getattr(request, 'user', None)
        
        if not user or not hasattr(user, 'id') or not isinstance(user, User):
            return Response({
                'authenticated': False,
                'user': None,
                'roles': [],
                'azure_ad_roles': [],
                'permissions': []
            })
        
        permissions = get_user_permissions(user)
        azure_ad_roles = getattr(user, 'azure_ad_roles', []) or []
        
        return Response({
            'authenticated': True,
            'user': {
                'id': str(user.id),
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'full_name': user.get_full_name(),
                'role': user.role,
                'role_display': user.get_role_display(),
                'user_type': getattr(user, 'user_type', 'internal'),
                'department': user.department,
                'is_admin': user.is_admin,
                'is_executive': user.is_executive,
                'is_internal': getattr(user, 'is_internal', True),
            },
            'roles': [user.role],
            'azure_ad_roles': azure_ad_roles,
            'permissions': permissions,
        })


class UnifiedSearchView(APIView):
    """
    Unified search endpoint that queries across multiple entity types.
    Returns results grouped by entity type: contacts, products, orders, tickets
    """
    def get(self, request):
        query = request.query_params.get('q', '').strip()
        limit = int(request.query_params.get('limit', 5))
        
        if not query or len(query) < 2:
            return Response({
                'contacts': [],
                'products': [],
                'orders': [],
                'tickets': [],
                'total': 0
            })
        
        results = {
            'contacts': [],
            'products': [],
            'orders': [],
            'tickets': [],
        }
        
        from backend.apps.crm.models import Contact, Ticket
        from backend.apps.erp.models import Product, SalesOrder
        
        contacts = Contact.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(account__name__icontains=query)
        ).select_related('account')[:limit]
        
        results['contacts'] = [{
            'id': c.id,
            'type': 'contact',
            'title': f"{c.first_name} {c.last_name}",
            'subtitle': c.account.name if c.account else c.email,
            'email': c.email,
            'account_id': c.account.id if c.account else None,
        } for c in contacts]
        
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(sku__icontains=query) |
            Q(description__icontains=query)
        )[:limit]
        
        results['products'] = [{
            'id': p.id,
            'type': 'product',
            'title': p.name,
            'subtitle': p.sku,
            'sku': p.sku,
            'price': str(p.unit_price),
            'category': p.category,
        } for p in products]
        
        orders = SalesOrder.objects.filter(
            Q(order_number__icontains=query) |
            Q(account__name__icontains=query)
        ).select_related('account')[:limit]
        
        results['orders'] = [{
            'id': o.id,
            'type': 'order',
            'title': o.order_number,
            'subtitle': o.account.name if o.account else 'No Account',
            'status': o.status,
            'total': str(o.total_amount) if o.total_amount else '0',
        } for o in orders]
        
        tickets = Ticket.objects.filter(
            Q(ticket_number__icontains=query) |
            Q(subject__icontains=query) |
            Q(account__name__icontains=query)
        ).select_related('account')[:limit]
        
        results['tickets'] = [{
            'id': t.id,
            'type': 'ticket',
            'title': t.subject,
            'subtitle': t.ticket_number,
            'status': t.status,
            'priority': t.priority,
            'account_id': t.account.id if t.account else None,
        } for t in tickets]
        
        results['total'] = (
            len(results['contacts']) + 
            len(results['products']) + 
            len(results['orders']) + 
            len(results['tickets'])
        )
        
        return Response(results)


class FavoriteViewSet(viewsets.ModelViewSet):
    """
    Manage user favorites for quick access to frequently used records.
    """
    queryset = Favorite.objects.all().order_by('-created_at')
    serializer_class = FavoriteSerializer
    
    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        queryset = Favorite.objects.all().order_by('-created_at')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        return queryset


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by('-created_at')
    serializer_class = EventSerializer


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all().order_by('-created_at')
    serializer_class = AuditLogSerializer


class HealthCheckView(APIView):
    """
    Health check endpoints for Kubernetes liveness and readiness probes.
    """
    def get(self, request, check_type='liveness'):
        from django.db import connection
        from django.core.cache import cache
        
        health = {
            'status': 'healthy',
            'timestamp': __import__('datetime').datetime.utcnow().isoformat(),
            'checks': {}
        }
        
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
            health['checks']['database'] = 'healthy'
        except Exception as e:
            health['checks']['database'] = f'unhealthy: {str(e)}'
            health['status'] = 'unhealthy'
        
        if check_type == 'readiness':
            try:
                cache.set('health_check', 'ok', 10)
                if cache.get('health_check') == 'ok':
                    health['checks']['cache'] = 'healthy'
                else:
                    health['checks']['cache'] = 'degraded'
            except Exception as e:
                health['checks']['cache'] = f'unavailable: {str(e)}'
        
        status_code = 200 if health['status'] == 'healthy' else 503
        return Response(health, status=status_code)


class CacheStatsView(APIView):
    """
    View Redis cache statistics for monitoring.
    """
    def get(self, request):
        from backend.apps.core.cache import CacheStats
        return Response(CacheStats.get_info())


class SecurityEventsView(APIView):
    """
    View security events for monitoring and incident response.
    Requires system_admin or executive role.
    """
    permission_classes = [IsSystemAdmin]
    
    def get(self, request):
        user_id = request.session.get('user_id')
        if not user_id:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            user = User.objects.get(id=user_id)
            if user.role not in ['system_admin', 'executive']:
                SecurityLogger.log(
                    SecurityEventType.PERMISSION_DENIED,
                    user_id=str(user.id),
                    endpoint='/api/v1/security/events/',
                    method='GET',
                    status_code=403,
                    severity='WARNING'
                )
                return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_401_UNAUTHORIZED)
        
        event_type = request.query_params.get('type')
        filter_user_id = request.query_params.get('user_id')
        limit = int(request.query_params.get('limit', 100))
        
        events = SecurityLogger.get_recent_events(
            event_type=event_type,
            user_id=filter_user_id,
            limit=limit
        )
        
        return Response({
            'events': events,
            'total': len(events),
            'event_types': [
                SecurityEventType.LOGIN_SUCCESS,
                SecurityEventType.LOGIN_FAILED,
                SecurityEventType.LOGOUT,
                SecurityEventType.TOKEN_BLACKLISTED,
                SecurityEventType.PERMISSION_DENIED,
                SecurityEventType.RATE_LIMIT_EXCEEDED,
                SecurityEventType.BRUTE_FORCE_DETECTED,
                SecurityEventType.ANOMALY_DETECTED,
                SecurityEventType.DATA_MODIFIED,
                SecurityEventType.DATA_DELETED,
                SecurityEventType.SENSITIVE_ACCESS,
                SecurityEventType.AFTER_HOURS_ACCESS,
            ]
        })


class SecurityDashboardView(APIView):
    """
    Security dashboard with metrics and alerts.
    Provides summary of security events for monitoring.
    """
    permission_classes = [IsSystemAdmin]
    
    def get(self, request):
        user_id = request.session.get('user_id')
        if not user_id:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            user = User.objects.get(id=user_id)
            if user.role not in ['system_admin', 'executive']:
                return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_401_UNAUTHORIZED)
        
        all_events = SecurityLogger.get_recent_events(limit=1000)
        
        event_counts = {}
        for event in all_events:
            event_type = event.get('event_type', 'UNKNOWN')
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        failed_logins = SecurityLogger.get_recent_events(
            event_type=SecurityEventType.LOGIN_FAILED,
            limit=100
        )
        
        brute_force = SecurityLogger.get_recent_events(
            event_type=SecurityEventType.BRUTE_FORCE_DETECTED,
            limit=10
        )
        
        anomalies = SecurityLogger.get_recent_events(
            event_type=SecurityEventType.ANOMALY_DETECTED,
            limit=10
        )
        
        permission_denials = SecurityLogger.get_recent_events(
            event_type=SecurityEventType.PERMISSION_DENIED,
            limit=100
        )
        
        severity_counts = {'INFO': 0, 'WARNING': 0, 'ERROR': 0, 'CRITICAL': 0}
        for event in all_events:
            severity = event.get('severity', 'INFO')
            if severity in severity_counts:
                severity_counts[severity] += 1
        
        critical_alerts = [e for e in all_events if e.get('severity') == 'CRITICAL'][:5]
        
        return Response({
            'summary': {
                'total_events': len(all_events),
                'event_counts': event_counts,
                'severity_counts': severity_counts,
            },
            'alerts': {
                'failed_logins': len(failed_logins),
                'brute_force_attempts': len(brute_force),
                'anomalies_detected': len(anomalies),
                'permission_denials': len(permission_denials),
                'critical_events': len(critical_alerts),
            },
            'recent_critical': critical_alerts,
            'recent_brute_force': brute_force,
            'recent_anomalies': anomalies,
        })


class ForceLogoutView(APIView):
    """
    Force logout a user by invalidating all their tokens.
    Requires system_admin role.
    """
    permission_classes = [IsSystemAdmin]
    
    def post(self, request):
        admin_user_id = request.session.get('user_id')
        if not admin_user_id:
            SecurityLogger.log(
                SecurityEventType.PERMISSION_DENIED,
                endpoint='/api/v1/security/force-logout/',
                method='POST',
                status_code=401,
                severity='WARNING',
                details={'reason': 'no_session'}
            )
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            admin_user = User.objects.get(id=admin_user_id)
            if admin_user.role != 'system_admin':
                SecurityLogger.log(
                    SecurityEventType.PERMISSION_DENIED,
                    user_id=str(admin_user.id),
                    endpoint='/api/v1/security/force-logout/',
                    method='POST',
                    status_code=403,
                    severity='WARNING',
                    details={'reason': 'insufficient_privileges', 'role': admin_user.role}
                )
                return Response({'error': 'Access denied. System admin role required.'}, status=status.HTTP_403_FORBIDDEN)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_401_UNAUTHORIZED)
        
        target_user_id = request.data.get('user_id')
        if not target_user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            target_user = User.objects.get(id=target_user_id)
        except User.DoesNotExist:
            return Response({'error': 'Target user not found'}, status=status.HTTP_404_NOT_FOUND)
        
        success = TokenBlacklist.blacklist_all_user_tokens(
            str(target_user.id),
            reason=f'forced_logout_by_{admin_user.username}'
        )
        
        if not success:
            return Response(
                {'error': 'Failed to invalidate tokens. Please try again.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        SecurityLogger.log(
            SecurityEventType.TOKEN_BLACKLISTED,
            user_id=str(admin_user.id),
            endpoint='/api/v1/security/force-logout/',
            method='POST',
            status_code=200,
            details={
                'action': 'force_logout',
                'target_user_id': str(target_user.id),
                'target_username': target_user.username,
                'initiated_by': admin_user.username,
            },
            severity='WARNING'
        )
        
        return Response({
            'success': True,
            'message': f'User {target_user.username} has been forcefully logged out',
            'user_id': str(target_user.id),
            'tokens_invalidated': True,
        })
