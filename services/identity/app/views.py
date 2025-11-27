"""
Views for Identity/Contact Service.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import User, Account, Contact, Address, AuditLog, Favorite, Event
from .serializers import (
    UserSerializer, AccountSerializer, AccountLookupSerializer,
    ContactSerializer, AddressSerializer, AuditLogSerializer,
    FavoriteSerializer, EventSerializer
)


class AuthMeView(APIView):
    """Return current authenticated user's profile, roles, and permissions."""
    
    def get(self, request):
        user = getattr(request, 'user', None)
        
        if not user or not hasattr(user, 'id') or not isinstance(user, User):
            return Response({
                'authenticated': False,
                'user': None,
                'roles': [],
                'azure_ad_roles': [],
                'permissions': []
            })
        
        permission_map = {
            'admin': ['all'],
            'Administrator': ['all'],
            'executive': ['read_all', 'reports', 'analytics'],
            'Executive': ['read_all', 'reports', 'analytics'],
            'finance': ['invoices', 'payments', 'budgets', 'financial_reports'],
            'Finance_User': ['invoices', 'payments', 'budgets', 'financial_reports'],
            'hr': ['employees', 'payroll', 'hr_records'],
            'HR_Manager': ['employees', 'payroll', 'hr_records'],
            'operations': ['inventory', 'warehouses', 'equipment', 'orders'],
            'Operations_Specialist': ['inventory', 'warehouses', 'equipment', 'orders'],
            'site_manager': ['projects', 'safety', 'site_equipment', 'site_documents'],
            'Site_Manager': ['projects', 'safety', 'site_equipment', 'site_documents'],
        }
        
        permissions = set()
        user_roles = getattr(user, 'roles', [user.role]) if hasattr(user, 'role') else []
        for role in user_roles:
            role_perms = permission_map.get(role, [])
            permissions.update(role_perms)
        
        azure_ad_roles = getattr(user, 'azure_ad_roles', []) or []
        
        return Response({
            'authenticated': True,
            'user': {
                'id': str(user.id),
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'full_name': f"{user.first_name or ''} {user.last_name or ''}".strip(),
                'role': user.role,
                'department': user.department,
                'is_active': user.is_active,
            },
            'roles': user_roles,
            'azure_ad_roles': azure_ad_roles,
            'permissions': list(permissions),
        })


class UserViewSet(viewsets.ModelViewSet):
    """API endpoints for user management."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['role', 'department', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']


class AccountViewSet(viewsets.ModelViewSet):
    """API endpoints for account management."""
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['type', 'tier', 'status', 'industry']
    search_fields = ['name', 'account_number', 'email']
    
    @action(detail=False, methods=['get'])
    def lookup(self, request):
        """Autocomplete lookup for accounts."""
        term = request.query_params.get('term', '')
        limit = int(request.query_params.get('limit', 10))
        
        if len(term) < 2:
            return Response([])
        
        accounts = Account.objects.filter(
            Q(name__icontains=term) | Q(account_number__icontains=term)
        )[:limit]
        
        serializer = AccountLookupSerializer(accounts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def related(self, request, pk=None):
        """Get related data for an account (for contextual side panel)."""
        account = self.get_object()
        
        contacts = account.contacts.all()[:5]
        
        return Response({
            'open_tickets': [],
            'open_tickets_count': 0,
            'recent_invoices': [],
            'total_invoices': 0,
            'contacts': ContactSerializer(contacts, many=True).data,
            'total_contacts': account.contacts.count(),
        })


class ContactViewSet(viewsets.ModelViewSet):
    """API endpoints for contact management."""
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['account', 'is_primary', 'is_active']
    search_fields = ['first_name', 'last_name', 'email']


class AddressViewSet(viewsets.ModelViewSet):
    """API endpoints for address management."""
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['account', 'contact', 'type', 'is_primary']


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoints for audit logs (read-only)."""
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'action', 'entity_type']


class FavoriteViewSet(viewsets.ModelViewSet):
    """API endpoints for user favorites."""
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'entity_type']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        return queryset


class EventViewSet(viewsets.ModelViewSet):
    """API endpoints for domain events."""
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['event_type', 'status', 'source_service']
