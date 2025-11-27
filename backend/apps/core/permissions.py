"""
Role-Based Access Control (RBAC) Permission Classes for Django REST Framework.

Implements comprehensive RBAC with 11 user roles:
- System Admin: Full system access
- Finance Manager: Financial data, auditing, payments
- Sales Representative: CRM, leads, opportunities
- Operations Specialist: Inventory, logistics, procurement
- Site Manager: Project execution, labor, safety
- HR Specialist: Employee records, payroll
- Warehouse Clerk: Inventory at assigned locations
- Field Worker: Own timecard and tasks
- Subcontractor/Vendor: Own POs and invoices
- Client/Customer: Own project data
- Executive Viewer: Read-only global access

Enforces:
- Principle of least privilege
- Segregation of Duties (SoD)
- Record-level access controls
"""

from rest_framework import permissions


ROLE_SYSTEM_ADMIN = 'system_admin'
ROLE_FINANCE_MANAGER = 'finance_manager'
ROLE_SALES_REP = 'sales_rep'
ROLE_OPERATIONS_SPECIALIST = 'operations_specialist'
ROLE_SITE_MANAGER = 'site_manager'
ROLE_HR_SPECIALIST = 'hr_specialist'
ROLE_WAREHOUSE_CLERK = 'warehouse_clerk'
ROLE_FIELD_WORKER = 'field_worker'
ROLE_SUBCONTRACTOR = 'subcontractor'
ROLE_CLIENT = 'client'
ROLE_EXECUTIVE = 'executive'

INTERNAL_ROLES = [
    ROLE_SYSTEM_ADMIN, ROLE_FINANCE_MANAGER, ROLE_SALES_REP,
    ROLE_OPERATIONS_SPECIALIST, ROLE_SITE_MANAGER, ROLE_HR_SPECIALIST,
    ROLE_WAREHOUSE_CLERK, ROLE_FIELD_WORKER, ROLE_EXECUTIVE
]

EXTERNAL_ROLES = [ROLE_SUBCONTRACTOR, ROLE_CLIENT]

GLOBAL_READ_ROLES = [ROLE_SYSTEM_ADMIN, ROLE_EXECUTIVE]
GLOBAL_WRITE_ROLES = [ROLE_SYSTEM_ADMIN]


RBAC_MATRIX = {
    'accounts': {
        ROLE_SYSTEM_ADMIN: {'read': True, 'write': True, 'delete': True},
        ROLE_FINANCE_MANAGER: {'read': True, 'write': True, 'delete': False},
        ROLE_SALES_REP: {'read': 'assigned', 'write': 'assigned', 'delete': False},
        ROLE_OPERATIONS_SPECIALIST: {'read': True, 'write': False, 'delete': False},
        ROLE_SITE_MANAGER: {'read': 'assigned', 'write': False, 'delete': False},
        ROLE_HR_SPECIALIST: {'read': False, 'write': False, 'delete': False},
        ROLE_WAREHOUSE_CLERK: {'read': False, 'write': False, 'delete': False},
        ROLE_FIELD_WORKER: {'read': False, 'write': False, 'delete': False},
        ROLE_SUBCONTRACTOR: {'read': 'own', 'write': False, 'delete': False},
        ROLE_CLIENT: {'read': 'own', 'write': False, 'delete': False},
        ROLE_EXECUTIVE: {'read': True, 'write': False, 'delete': False},
    },
    'projects': {
        ROLE_SYSTEM_ADMIN: {'read': True, 'write': True, 'delete': True},
        ROLE_FINANCE_MANAGER: {'read': True, 'write': False, 'delete': False},
        ROLE_SALES_REP: {'read': 'assigned', 'write': False, 'delete': False},
        ROLE_OPERATIONS_SPECIALIST: {'read': True, 'write': True, 'delete': False},
        ROLE_SITE_MANAGER: {'read': 'assigned', 'write': 'assigned', 'delete': False},
        ROLE_HR_SPECIALIST: {'read': True, 'write': False, 'delete': False},
        ROLE_WAREHOUSE_CLERK: {'read': False, 'write': False, 'delete': False},
        ROLE_FIELD_WORKER: {'read': 'assigned', 'write': False, 'delete': False},
        ROLE_SUBCONTRACTOR: {'read': 'assigned', 'write': False, 'delete': False},
        ROLE_CLIENT: {'read': 'own', 'write': False, 'delete': False},
        ROLE_EXECUTIVE: {'read': True, 'write': False, 'delete': False},
    },
    'invoices': {
        ROLE_SYSTEM_ADMIN: {'read': True, 'write': True, 'delete': True},
        ROLE_FINANCE_MANAGER: {'read': True, 'write': True, 'delete': False},
        ROLE_SALES_REP: {'read': 'assigned', 'write': False, 'delete': False},
        ROLE_OPERATIONS_SPECIALIST: {'read': True, 'write': False, 'delete': False},
        ROLE_SITE_MANAGER: {'read': 'assigned', 'write': False, 'delete': False},
        ROLE_HR_SPECIALIST: {'read': False, 'write': False, 'delete': False},
        ROLE_WAREHOUSE_CLERK: {'read': False, 'write': False, 'delete': False},
        ROLE_FIELD_WORKER: {'read': False, 'write': False, 'delete': False},
        ROLE_SUBCONTRACTOR: {'read': 'own', 'write': 'create_only', 'delete': False},
        ROLE_CLIENT: {'read': 'own', 'write': False, 'delete': False},
        ROLE_EXECUTIVE: {'read': True, 'write': False, 'delete': False},
    },
    'orders': {
        ROLE_SYSTEM_ADMIN: {'read': True, 'write': True, 'delete': True},
        ROLE_FINANCE_MANAGER: {'read': True, 'write': 'payment_status', 'delete': False},
        ROLE_SALES_REP: {'read': 'assigned', 'write': 'assigned', 'delete': False},
        ROLE_OPERATIONS_SPECIALIST: {'read': True, 'write': 'fulfillment_status', 'delete': False},
        ROLE_SITE_MANAGER: {'read': 'assigned', 'write': False, 'delete': False},
        ROLE_HR_SPECIALIST: {'read': False, 'write': False, 'delete': False},
        ROLE_WAREHOUSE_CLERK: {'read': 'assigned', 'write': False, 'delete': False},
        ROLE_FIELD_WORKER: {'read': False, 'write': False, 'delete': False},
        ROLE_SUBCONTRACTOR: {'read': 'own', 'write': False, 'delete': False},
        ROLE_CLIENT: {'read': 'own', 'write': False, 'delete': False},
        ROLE_EXECUTIVE: {'read': True, 'write': False, 'delete': False},
    },
    'inventory': {
        ROLE_SYSTEM_ADMIN: {'read': True, 'write': True, 'delete': True},
        ROLE_FINANCE_MANAGER: {'read': True, 'write': False, 'delete': False},
        ROLE_SALES_REP: {'read': True, 'write': False, 'delete': False},
        ROLE_OPERATIONS_SPECIALIST: {'read': True, 'write': True, 'delete': False},
        ROLE_SITE_MANAGER: {'read': 'assigned', 'write': False, 'delete': False},
        ROLE_HR_SPECIALIST: {'read': False, 'write': False, 'delete': False},
        ROLE_WAREHOUSE_CLERK: {'read': 'warehouse', 'write': 'warehouse', 'delete': False},
        ROLE_FIELD_WORKER: {'read': False, 'write': False, 'delete': False},
        ROLE_SUBCONTRACTOR: {'read': False, 'write': False, 'delete': False},
        ROLE_CLIENT: {'read': False, 'write': False, 'delete': False},
        ROLE_EXECUTIVE: {'read': True, 'write': False, 'delete': False},
    },
    'employees': {
        ROLE_SYSTEM_ADMIN: {'read': True, 'write': True, 'delete': True},
        ROLE_FINANCE_MANAGER: {'read': True, 'write': False, 'delete': False},
        ROLE_SALES_REP: {'read': False, 'write': False, 'delete': False},
        ROLE_OPERATIONS_SPECIALIST: {'read': True, 'write': False, 'delete': False},
        ROLE_SITE_MANAGER: {'read': 'assigned', 'write': False, 'delete': False},
        ROLE_HR_SPECIALIST: {'read': True, 'write': True, 'delete': False},
        ROLE_WAREHOUSE_CLERK: {'read': False, 'write': False, 'delete': False},
        ROLE_FIELD_WORKER: {'read': 'own', 'write': 'own', 'delete': False},
        ROLE_SUBCONTRACTOR: {'read': False, 'write': False, 'delete': False},
        ROLE_CLIENT: {'read': False, 'write': False, 'delete': False},
        ROLE_EXECUTIVE: {'read': True, 'write': False, 'delete': False},
    },
    'safety': {
        ROLE_SYSTEM_ADMIN: {'read': True, 'write': True, 'delete': True},
        ROLE_FINANCE_MANAGER: {'read': True, 'write': False, 'delete': False},
        ROLE_SALES_REP: {'read': False, 'write': False, 'delete': False},
        ROLE_OPERATIONS_SPECIALIST: {'read': True, 'write': True, 'delete': False},
        ROLE_SITE_MANAGER: {'read': 'assigned', 'write': 'assigned', 'delete': False},
        ROLE_HR_SPECIALIST: {'read': True, 'write': False, 'delete': False},
        ROLE_WAREHOUSE_CLERK: {'read': 'warehouse', 'write': False, 'delete': False},
        ROLE_FIELD_WORKER: {'read': 'assigned', 'write': False, 'delete': False},
        ROLE_SUBCONTRACTOR: {'read': 'assigned', 'write': False, 'delete': False},
        ROLE_CLIENT: {'read': False, 'write': False, 'delete': False},
        ROLE_EXECUTIVE: {'read': True, 'write': False, 'delete': False},
    },
    'reports': {
        ROLE_SYSTEM_ADMIN: {'read': True, 'write': True, 'delete': True},
        ROLE_FINANCE_MANAGER: {'read': True, 'write': True, 'delete': False},
        ROLE_SALES_REP: {'read': 'assigned', 'write': False, 'delete': False},
        ROLE_OPERATIONS_SPECIALIST: {'read': True, 'write': True, 'delete': False},
        ROLE_SITE_MANAGER: {'read': 'assigned', 'write': False, 'delete': False},
        ROLE_HR_SPECIALIST: {'read': True, 'write': True, 'delete': False},
        ROLE_WAREHOUSE_CLERK: {'read': 'warehouse', 'write': False, 'delete': False},
        ROLE_FIELD_WORKER: {'read': False, 'write': False, 'delete': False},
        ROLE_SUBCONTRACTOR: {'read': False, 'write': False, 'delete': False},
        ROLE_CLIENT: {'read': 'own', 'write': False, 'delete': False},
        ROLE_EXECUTIVE: {'read': True, 'write': False, 'delete': False},
    },
}


class IsAuthenticated(permissions.BasePermission):
    """Permission class that requires user authentication."""
    message = 'Authentication required.'
    
    def has_permission(self, request, view):
        return bool(request.user and hasattr(request.user, 'id'))


class IsSystemAdmin(permissions.BasePermission):
    """Permission for System Administrator - full access."""
    message = 'System Administrator access required.'
    
    def has_permission(self, request, view):
        if not request.user or not hasattr(request.user, 'role'):
            return False
        return request.user.role == ROLE_SYSTEM_ADMIN


class IsFinanceManager(permissions.BasePermission):
    """Permission for Finance Manager - financial data access."""
    message = 'Finance Manager access required.'
    
    def has_permission(self, request, view):
        if not request.user or not hasattr(request.user, 'role'):
            return False
        allowed = [ROLE_SYSTEM_ADMIN, ROLE_FINANCE_MANAGER]
        return request.user.role in allowed


class IsSalesRep(permissions.BasePermission):
    """Permission for Sales Representative - CRM access."""
    message = 'Sales Representative access required.'
    
    def has_permission(self, request, view):
        if not request.user or not hasattr(request.user, 'role'):
            return False
        allowed = [ROLE_SYSTEM_ADMIN, ROLE_SALES_REP, ROLE_FINANCE_MANAGER]
        return request.user.role in allowed


class IsOperationsSpecialist(permissions.BasePermission):
    """Permission for Operations Specialist - inventory/logistics access."""
    message = 'Operations Specialist access required.'
    
    def has_permission(self, request, view):
        if not request.user or not hasattr(request.user, 'role'):
            return False
        allowed = [ROLE_SYSTEM_ADMIN, ROLE_OPERATIONS_SPECIALIST]
        return request.user.role in allowed


class IsSiteManager(permissions.BasePermission):
    """Permission for Site Manager - project execution access."""
    message = 'Site Manager access required.'
    
    def has_permission(self, request, view):
        if not request.user or not hasattr(request.user, 'role'):
            return False
        allowed = [ROLE_SYSTEM_ADMIN, ROLE_SITE_MANAGER, ROLE_OPERATIONS_SPECIALIST]
        return request.user.role in allowed


class IsHRSpecialist(permissions.BasePermission):
    """Permission for HR Specialist - employee data access."""
    message = 'HR Specialist access required.'
    
    def has_permission(self, request, view):
        if not request.user or not hasattr(request.user, 'role'):
            return False
        allowed = [ROLE_SYSTEM_ADMIN, ROLE_HR_SPECIALIST]
        return request.user.role in allowed


class IsWarehouseClerk(permissions.BasePermission):
    """Permission for Warehouse Clerk - inventory at assigned location."""
    message = 'Warehouse Clerk access required.'
    
    def has_permission(self, request, view):
        if not request.user or not hasattr(request.user, 'role'):
            return False
        allowed = [ROLE_SYSTEM_ADMIN, ROLE_WAREHOUSE_CLERK, ROLE_OPERATIONS_SPECIALIST]
        return request.user.role in allowed


class IsFieldWorker(permissions.BasePermission):
    """Permission for Field Worker - own timecard/tasks."""
    message = 'Field Worker access required.'
    
    def has_permission(self, request, view):
        if not request.user or not hasattr(request.user, 'role'):
            return False
        return request.user.role in INTERNAL_ROLES


class IsSubcontractor(permissions.BasePermission):
    """Permission for Subcontractor/Vendor - own POs and invoices."""
    message = 'Subcontractor access required.'
    
    def has_permission(self, request, view):
        if not request.user or not hasattr(request.user, 'role'):
            return False
        allowed = [ROLE_SYSTEM_ADMIN, ROLE_SUBCONTRACTOR, ROLE_OPERATIONS_SPECIALIST]
        return request.user.role in allowed


class IsClient(permissions.BasePermission):
    """Permission for Client/Customer Portal - own project data."""
    message = 'Client access required.'
    
    def has_permission(self, request, view):
        if not request.user or not hasattr(request.user, 'role'):
            return False
        allowed = [ROLE_SYSTEM_ADMIN, ROLE_CLIENT, ROLE_SALES_REP]
        return request.user.role in allowed


class IsExecutive(permissions.BasePermission):
    """Permission for Executive Viewer - global read access."""
    message = 'Executive access required.'
    
    def has_permission(self, request, view):
        if not request.user or not hasattr(request.user, 'role'):
            return False
        allowed = [ROLE_SYSTEM_ADMIN, ROLE_EXECUTIVE]
        return request.user.role in allowed


class IsInternalUser(permissions.BasePermission):
    """Permission for any internal staff member."""
    message = 'Internal staff access required.'
    
    def has_permission(self, request, view):
        if not request.user or not hasattr(request.user, 'role'):
            return False
        return request.user.role in INTERNAL_ROLES


class IsExternalUser(permissions.BasePermission):
    """Permission for external users (subcontractors, clients)."""
    message = 'External user access.'
    
    def has_permission(self, request, view):
        if not request.user or not hasattr(request.user, 'role'):
            return False
        return request.user.role in EXTERNAL_ROLES


class ReadOnly(permissions.BasePermission):
    """Permission that allows read-only access."""
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class GlobalReadOrOwner(permissions.BasePermission):
    """
    Global read for executives/admins, or owner-only access for others.
    """
    def has_permission(self, request, view):
        if not request.user or not hasattr(request.user, 'role'):
            return False
        return True
    
    def has_object_permission(self, request, view, obj):
        if not request.user or not hasattr(request.user, 'role'):
            return False
        
        if request.user.role in GLOBAL_READ_ROLES:
            return True
        
        owner_id = None
        for field in ['user_id', 'owner_id', 'account_id', 'vendor_id', 'created_by']:
            if hasattr(obj, field):
                owner_id = getattr(obj, field)
                break
        
        if owner_id:
            user_id = str(request.user.id)
            if str(owner_id) == user_id:
                return True
            if hasattr(request.user, 'vendor_id') and str(owner_id) == str(request.user.vendor_id):
                return True
        
        return False


class ProjectAssignmentPermission(permissions.BasePermission):
    """Permission based on project assignment."""
    
    def has_object_permission(self, request, view, obj):
        if not request.user or not hasattr(request.user, 'role'):
            return False
        
        if request.user.role in GLOBAL_READ_ROLES:
            return True
        
        project_id = getattr(obj, 'project_id', None) or getattr(obj, 'id', None)
        
        if project_id:
            return request.user.can_access_project(project_id)
        
        return False


class WarehouseAssignmentPermission(permissions.BasePermission):
    """Permission based on warehouse assignment for clerks."""
    
    def has_object_permission(self, request, view, obj):
        if not request.user or not hasattr(request.user, 'role'):
            return False
        
        if request.user.role in GLOBAL_READ_ROLES:
            return True
        
        if request.user.role == ROLE_OPERATIONS_SPECIALIST:
            return True
        
        warehouse_id = getattr(obj, 'warehouse_id', None) or getattr(obj, 'id', None)
        
        if warehouse_id and request.user.role == ROLE_WAREHOUSE_CLERK:
            return request.user.can_access_warehouse(warehouse_id)
        
        return False


class SegregationOfDuties(permissions.BasePermission):
    """
    Enforces Segregation of Duties (SoD).
    Finance can only update payment fields, Operations can only update fulfillment fields.
    """
    
    FINANCE_FIELDS = ['invoice_payment_status', 'payment_status', 'payment_date', 'payment_amount']
    OPERATIONS_FIELDS = ['order_fulfillment_status', 'fulfillment_status', 'shipped_date', 'delivery_date']
    
    def has_permission(self, request, view):
        if request.method not in ['PUT', 'PATCH']:
            return True
        
        if not request.user or not hasattr(request.user, 'role'):
            return False
        
        if request.user.role == ROLE_SYSTEM_ADMIN:
            return True
        
        if not request.data:
            return True
        
        updating_fields = set(request.data.keys())
        
        if request.user.role == ROLE_FINANCE_MANAGER:
            if updating_fields.intersection(self.OPERATIONS_FIELDS):
                self.message = 'Finance Manager cannot modify fulfillment fields.'
                return False
        
        if request.user.role == ROLE_OPERATIONS_SPECIALIST:
            if updating_fields.intersection(self.FINANCE_FIELDS):
                self.message = 'Operations Specialist cannot modify payment fields.'
                return False
        
        return True


class HasResourcePermission(permissions.BasePermission):
    """
    Dynamic permission based on RBAC matrix.
    
    Usage:
        class MyViewSet(viewsets.ModelViewSet):
            permission_classes = [HasResourcePermission]
            resource_name = 'accounts'
    """
    
    def has_permission(self, request, view):
        if not request.user or not hasattr(request.user, 'role'):
            return False
        
        resource = getattr(view, 'resource_name', None)
        if not resource or resource not in RBAC_MATRIX:
            return True
        
        role = request.user.role
        if role not in RBAC_MATRIX[resource]:
            return False
        
        perms = RBAC_MATRIX[resource][role]
        
        if request.method in permissions.SAFE_METHODS:
            return perms.get('read', False) not in [False, None]
        
        if request.method == 'DELETE':
            return perms.get('delete', False) == True
        
        return perms.get('write', False) not in [False, None]


class AllowAnyForRead(permissions.BasePermission):
    """Allow read access without authentication."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and hasattr(request.user, 'id'))


def role_required(*roles):
    """
    Decorator for function-based views that requires specific roles.
    """
    def decorator(view_func):
        def wrapped_view(request, *args, **kwargs):
            if not request.user or not hasattr(request.user, 'role'):
                from rest_framework.response import Response
                return Response({'detail': 'Authentication required.'}, status=401)
            
            if request.user.role not in roles and ROLE_SYSTEM_ADMIN not in roles:
                if request.user.role != ROLE_SYSTEM_ADMIN:
                    from rest_framework.response import Response
                    return Response(
                        {'detail': f'Required role: {", ".join(roles)}'},
                        status=403
                    )
            
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator


def get_user_permissions(user):
    """
    Returns a dict of all permissions for a user based on their role.
    """
    if not user or not hasattr(user, 'role'):
        return {}
    
    role = user.role
    permissions_dict = {}
    
    for resource, role_perms in RBAC_MATRIX.items():
        if role in role_perms:
            permissions_dict[resource] = role_perms[role]
    
    return permissions_dict
