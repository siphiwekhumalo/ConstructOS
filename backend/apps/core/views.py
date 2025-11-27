from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.db.models import Q
from .models import User, Event, AuditLog, Favorite
from .serializers import UserSerializer, UserCreateSerializer, EventSerializer, AuditLogSerializer, FavoriteSerializer
from .permissions import IsAuthenticated, IsSystemAdmin, IsFinanceManager, IsHRSpecialist, get_user_permissions


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
