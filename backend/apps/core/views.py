from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.authentication import SessionAuthentication
from django.db.models import Q
from django.db import models
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
from backend.apps.construction.models import Project, Transaction
from datetime import timedelta
from django.utils import timezone


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
    Requires system_admin role via DRF permission class.
    
    DRF handles authentication and permission checks automatically.
    If user is not authenticated, DRF returns 401.
    If user lacks permission, IsSystemAdmin returns 403.
    """
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsSystemAdmin]
    
    def get(self, request):
        user = request.user
        
        SecurityLogger.log(
            SecurityEventType.SENSITIVE_ACCESS,
            user_id=str(user.id),
            endpoint='/api/v1/security/events/',
            method='GET',
            status_code=200,
            severity='INFO',
            details={'action': 'view_security_events'}
        )
        
        event_type = request.query_params.get('type')
        filter_user_id = request.query_params.get('user_id')
        
        try:
            limit = min(int(request.query_params.get('limit', 100)), 1000)
        except (ValueError, TypeError):
            limit = 100
        
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
        }, status=status.HTTP_200_OK)


class SecurityDashboardView(APIView):
    """
    Security dashboard with metrics and alerts.
    Provides summary of security events for monitoring.
    
    DRF handles authentication and permission checks automatically.
    """
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsSystemAdmin]
    
    def get(self, request):
        user = request.user
        
        SecurityLogger.log(
            SecurityEventType.SENSITIVE_ACCESS,
            user_id=str(user.id),
            endpoint='/api/v1/security/dashboard/',
            method='GET',
            status_code=200,
            severity='INFO',
            details={'action': 'view_security_dashboard'}
        )
        
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
        }, status=status.HTTP_200_OK)


class ForceLogoutView(APIView):
    """
    Force logout a user by invalidating all their tokens.
    Requires system_admin role via DRF permission class.
    
    DRF handles authentication and permission checks automatically.
    """
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsSystemAdmin]
    
    def post(self, request):
        admin_user = request.user
        
        target_user_id = request.data.get('user_id')
        if not target_user_id:
            SecurityLogger.log(
                SecurityEventType.SENSITIVE_ACCESS,
                user_id=str(admin_user.id),
                endpoint='/api/v1/security/force-logout/',
                method='POST',
                status_code=400,
                severity='WARNING',
                details={'error': 'missing_user_id'}
            )
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from uuid import UUID
            UUID(str(target_user_id))
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid user_id format'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            target_user = User.objects.get(id=target_user_id)
        except User.DoesNotExist:
            SecurityLogger.log(
                SecurityEventType.SENSITIVE_ACCESS,
                user_id=str(admin_user.id),
                endpoint='/api/v1/security/force-logout/',
                method='POST',
                status_code=404,
                severity='INFO',
                details={'error': 'target_not_found', 'target_id': str(target_user_id)}
            )
            return Response(
                {'error': 'Target user not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if str(target_user.id) == str(admin_user.id):
            return Response(
                {'error': 'Cannot force logout yourself. Use the regular logout endpoint.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        success = TokenBlacklist.blacklist_all_user_tokens(
            str(target_user.id),
            reason=f'forced_logout_by_{admin_user.username}'
        )
        
        if not success:
            SecurityLogger.log(
                SecurityEventType.SENSITIVE_ACCESS,
                user_id=str(admin_user.id),
                endpoint='/api/v1/security/force-logout/',
                method='POST',
                status_code=500,
                severity='ERROR',
                details={
                    'error': 'token_blacklist_failed',
                    'target_user_id': str(target_user.id)
                }
            )
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
        }, status=status.HTTP_200_OK)


class DashboardFinanceSummaryView(APIView):
    def get(self, request):
        # Aggregate total contract value for all signed/active projects
        total_contract_value = Project.objects.filter(status__in=["Signed", "Active"]).aggregate(
            total=models.Sum("budget")
        )["total"] or 0
        # Net cash flow over last 90 days
        now = timezone.now()
        start_date = now - timedelta(days=90)
        transactions = Transaction.objects.filter(created_at__gte=start_date)
        income = transactions.filter(type="income").aggregate(total=models.Sum("amount"))["total"] or 0
        expense = transactions.filter(type="expense").aggregate(total=models.Sum("amount"))["total"] or 0
        net_cash_flow = float(income) - float(expense)
        # Project count for dashboard
        total_projects = Project.objects.count()
        # Client count for dashboard
        from backend.apps.crm.models import Account
        total_clients = Account.objects.filter(type="customer").count()
        # Employee count for dashboard
        from backend.apps.erp.models import Employee
        total_employees = Employee.objects.count()
        # Financial summary for dashboard
        total_expenses = Transaction.objects.filter(type="expense").aggregate(total=models.Sum("amount"))["total"] or 0
        return Response({
            "total_contract_value": float(total_contract_value),
            "net_cash_flow": net_cash_flow,
            "profit_margin": {"gross": 0.22, "net": 0.14},
            "projects": {"total": total_projects},
            "clients": {"total": total_clients},
            "employees": {"total": total_employees},
            "financial": {"totalExpenses": float(total_expenses)},
        })

class DashboardARDaysView(APIView):
    def get(self, request):
        return Response({"value": 38})

class DashboardProfitMarginView(APIView):
    def get(self, request):
        # Calculate profit margins from transactions
        total_income = Transaction.objects.filter(type="income").aggregate(total=models.Sum("amount"))["total"] or 0
        total_expense = Transaction.objects.filter(type="expense").aggregate(total=models.Sum("amount"))["total"] or 0
        gross_profit = float(total_income) - float(total_expense)
        gross_margin = (gross_profit / float(total_income)) if total_income else 0
        # For net margin, assume net income = gross profit (unless taxes/other are tracked)
        net_margin = gross_margin
        return Response({"gross": round(gross_margin, 2), "net": round(net_margin, 2)})

class DashboardCashFlowView(APIView):
    def get(self, request):
        return Response({"chart": [{"date": "2025-09-01", "in": 100000, "out": 80000}, {"date": "2025-10-01", "in": 120000, "out": 90000}]})

class DashboardTrendChartView(APIView):
    def get(self, request):
        return Response([{"month": "2025-01", "budget": 100000, "actual": 95000, "earned": 90000}, {"month": "2025-02", "budget": 120000, "actual": 110000, "earned": 105000}])

class DashboardReworkCostView(APIView):
    def get(self, request):
        return Response({"percent": 2.5})

class DashboardSafetySummaryView(APIView):
    def get(self, request):
        return Response({"ltir": 1.8, "benchmark": 1.2, "open_issues": 4})

class DashboardSPIMapView(APIView):
    def get(self, request):
        return Response({"on_time": 8, "at_risk": 3, "delayed": 2})

class DashboardResourceUtilizationView(APIView):
    def get(self, request):
        return Response({"percent": 76})

class DashboardProjectMapView(APIView):
    def get(self, request):
        return Response([
            {"site_id": "SIT-JHB-001", "lat": -26.2041, "lng": 28.0473, "status": "on_time", "name": "Johannesburg Office Tower"},
            {"site_id": "SIT-CPT-002", "lat": -33.9249, "lng": 18.4241, "status": "delayed", "name": "Cape Town Waterfront Hotel"},
            {"site_id": "SIT-PTA-004", "lat": -25.7479, "lng": 28.2293, "status": "at_risk", "name": "Pretoria Medical Centre"},
        ])
