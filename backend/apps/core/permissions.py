"""
Role-Based Access Control (RBAC) Permission Classes for Django REST Framework.

These permission classes enforce access control based on user roles from
Microsoft Entra ID and the local user database.
"""

from rest_framework import permissions


class IsAuthenticated(permissions.BasePermission):
    """
    Permission class that requires user authentication.
    """
    message = 'Authentication required.'
    
    def has_permission(self, request, view):
        return bool(request.user and hasattr(request.user, 'id'))


class IsAdmin(permissions.BasePermission):
    """
    Permission class that requires admin role.
    """
    message = 'Administrator access required.'
    
    def has_permission(self, request, view):
        if not request.user or not hasattr(request.user, 'roles'):
            return False
        return request.user.has_any_role(['admin', 'Administrator'])


class IsFinanceUser(permissions.BasePermission):
    """
    Permission class for Finance role.
    Finance users can access financial data, invoices, payments, and budgets.
    """
    message = 'Finance role required.'
    
    def has_permission(self, request, view):
        if not request.user or not hasattr(request.user, 'roles'):
            return False
        allowed_roles = ['finance', 'Finance_User', 'admin', 'Administrator', 'executive']
        return request.user.has_any_role(allowed_roles)


class IsHRManager(permissions.BasePermission):
    """
    Permission class for HR Manager role.
    HR Managers can access employee data, payroll, and HR functions.
    """
    message = 'HR Manager role required.'
    
    def has_permission(self, request, view):
        if not request.user or not hasattr(request.user, 'roles'):
            return False
        allowed_roles = ['hr', 'HR_Manager', 'admin', 'Administrator', 'executive']
        return request.user.has_any_role(allowed_roles)


class IsOperationsSpecialist(permissions.BasePermission):
    """
    Permission class for Operations role.
    Operations specialists can access inventory, warehouses, and logistics.
    """
    message = 'Operations role required.'
    
    def has_permission(self, request, view):
        if not request.user or not hasattr(request.user, 'roles'):
            return False
        allowed_roles = ['operations', 'Operations_Specialist', 'admin', 'Administrator', 'executive']
        return request.user.has_any_role(allowed_roles)


class IsSiteManager(permissions.BasePermission):
    """
    Permission class for Site Manager role.
    Site Managers can access project data and manage site-specific operations.
    They typically have restricted access to only their assigned sites.
    """
    message = 'Site Manager role required.'
    
    def has_permission(self, request, view):
        if not request.user or not hasattr(request.user, 'roles'):
            return False
        allowed_roles = ['site_manager', 'Site_Manager', 'admin', 'Administrator', 'executive', 'operations']
        return request.user.has_any_role(allowed_roles)


class IsExecutive(permissions.BasePermission):
    """
    Permission class for Executive role.
    Executives have read access to all data for oversight and reporting.
    """
    message = 'Executive role required.'
    
    def has_permission(self, request, view):
        if not request.user or not hasattr(request.user, 'roles'):
            return False
        allowed_roles = ['executive', 'Executive', 'admin', 'Administrator']
        return request.user.has_any_role(allowed_roles)


class ReadOnly(permissions.BasePermission):
    """
    Permission class that allows read-only access.
    Used in combination with other permissions using OR logic.
    """
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Object-level permission that allows owners or admins to modify objects.
    Requires the object to have a 'user' or 'owner' field.
    """
    message = 'You must be the owner or an admin to perform this action.'
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if not request.user or not hasattr(request.user, 'id'):
            return False
        
        if request.user.has_any_role(['admin', 'Administrator']):
            return True
        
        owner = getattr(obj, 'owner', None) or getattr(obj, 'user', None)
        if owner:
            owner_id = getattr(owner, 'id', owner)
            return str(owner_id) == str(request.user.id)
        
        return False


class HasRolePermission(permissions.BasePermission):
    """
    Dynamic permission class that checks against a list of allowed roles.
    
    Usage:
        class MyViewSet(viewsets.ModelViewSet):
            permission_classes = [HasRolePermission]
            allowed_roles = ['finance', 'admin']
    """
    message = 'You do not have permission to perform this action.'
    
    def has_permission(self, request, view):
        if not request.user or not hasattr(request.user, 'roles'):
            return False
        
        allowed_roles = getattr(view, 'allowed_roles', [])
        if not allowed_roles:
            return True
        
        return request.user.has_any_role(allowed_roles)


class AllowAnyForRead(permissions.BasePermission):
    """
    Allow read access without authentication.
    Require authentication for write operations.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and hasattr(request.user, 'id'))


def role_required(*roles):
    """
    Decorator for function-based views that requires specific roles.
    
    Usage:
        @api_view(['GET'])
        @role_required('finance', 'admin')
        def my_view(request):
            ...
    """
    def decorator(view_func):
        def wrapped_view(request, *args, **kwargs):
            if not request.user or not hasattr(request.user, 'roles'):
                from rest_framework.response import Response
                return Response(
                    {'detail': 'Authentication required.'},
                    status=401
                )
            
            if not request.user.has_any_role(roles):
                from rest_framework.response import Response
                return Response(
                    {'detail': f'Required role: {", ".join(roles)}'},
                    status=403
                )
            
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator
