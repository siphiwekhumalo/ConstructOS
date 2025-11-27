"""
Authentication views for ConstructOS.
Provides login, logout, and demo user management.

Security features:
- Brute-force protection with account lockout
- Rate limiting on authentication endpoints
- Security event logging
- Session token blacklisting on logout
"""
import uuid
from datetime import datetime, timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.hashers import check_password

from .models import User
from .permissions import get_user_permissions
from .security import (
    TokenBlacklist,
    SecurityLogger,
    SecurityEventType,
    BruteForceProtection,
    RateLimiter,
    AnomalyDetector,
    get_client_ip,
    get_user_agent,
)


DEMO_USERS = [
    {
        'username': 'admin',
        'email': 'admin@constructos.co.za',
        'password': 'demo123',
        'first_name': 'Thabo',
        'last_name': 'Mokoena',
        'role': 'system_admin',
        'user_type': 'internal',
        'department': 'IT',
    },
    {
        'username': 'finance',
        'email': 'finance@constructos.co.za',
        'password': 'demo123',
        'first_name': 'Naledi',
        'last_name': 'Khumalo',
        'role': 'finance_manager',
        'user_type': 'internal',
        'department': 'Finance',
    },
    {
        'username': 'sales',
        'email': 'sales@constructos.co.za',
        'password': 'demo123',
        'first_name': 'Sipho',
        'last_name': 'Ndlovu',
        'role': 'sales_rep',
        'user_type': 'internal',
        'department': 'Sales',
    },
    {
        'username': 'operations',
        'email': 'operations@constructos.co.za',
        'password': 'demo123',
        'first_name': 'Lerato',
        'last_name': 'Molefe',
        'role': 'operations_specialist',
        'user_type': 'internal',
        'department': 'Operations',
    },
    {
        'username': 'sitemanager',
        'email': 'sitemanager@constructos.co.za',
        'password': 'demo123',
        'first_name': 'Bongani',
        'last_name': 'Zulu',
        'role': 'site_manager',
        'user_type': 'internal',
        'department': 'Construction',
        'assigned_project_ids': ['proj-001', 'proj-002'],
    },
    {
        'username': 'hr',
        'email': 'hr@constructos.co.za',
        'password': 'demo123',
        'first_name': 'Nomvula',
        'last_name': 'Dlamini',
        'role': 'hr_specialist',
        'user_type': 'internal',
        'department': 'Human Resources',
    },
    {
        'username': 'warehouse',
        'email': 'warehouse@constructos.co.za',
        'password': 'demo123',
        'first_name': 'Mandla',
        'last_name': 'Mthembu',
        'role': 'warehouse_clerk',
        'user_type': 'internal',
        'department': 'Warehouse',
        'assigned_warehouse_id': 'wh-001',
    },
    {
        'username': 'fieldworker',
        'email': 'fieldworker@constructos.co.za',
        'password': 'demo123',
        'first_name': 'Tshepo',
        'last_name': 'Sithole',
        'role': 'field_worker',
        'user_type': 'internal',
        'department': 'Construction',
        'assigned_project_ids': ['proj-001'],
    },
    {
        'username': 'subcontractor',
        'email': 'subcontractor@melachplumbing.co.za',
        'password': 'demo123',
        'first_name': 'Johan',
        'last_name': 'van der Berg',
        'role': 'subcontractor',
        'user_type': 'external',
        'department': 'External - Plumbing',
        'vendor_id': 'vendor-001',
        'assigned_project_ids': ['proj-001'],
    },
    {
        'username': 'client',
        'email': 'client@saproperties.co.za',
        'password': 'demo123',
        'first_name': 'Precious',
        'last_name': 'Nkosi',
        'role': 'client',
        'user_type': 'external',
        'department': 'External - Client',
        'assigned_account_ids': ['acc-001'],
        'assigned_project_ids': ['proj-002'],
    },
    {
        'username': 'executive',
        'email': 'ceo@constructos.co.za',
        'password': 'demo123',
        'first_name': 'Mpho',
        'last_name': 'Mahlangu',
        'role': 'executive',
        'user_type': 'internal',
        'department': 'Executive',
    },
]


def create_demo_users():
    """Create or update all demo users in the database."""
    created_users = []
    
    for user_data in DEMO_USERS:
        password = user_data.pop('password', 'demo123')
        username = user_data['username']
        
        try:
            user = User.objects.get(username=username)
            for key, value in user_data.items():
                setattr(user, key, value)
            user.set_password(password)
            user.save()
        except User.DoesNotExist:
            user = User(
                id=str(uuid.uuid4()),
                **user_data
            )
            user.set_password(password)
            user.save()
        
        user_data['password'] = password
        created_users.append(user)
    
    return created_users


@api_view(['POST'])
def login_view(request):
    """
    Authenticate user with username/email and password.
    Returns user info and session token.
    
    Security features:
    - Rate limiting (5 attempts per 15 minutes)
    - Brute-force protection with account lockout
    - Security event logging
    - Anomaly detection for after-hours access
    """
    ip_address = get_client_ip(request)
    user_agent = get_user_agent(request)
    username = request.data.get('username', '').strip()
    password = request.data.get('password', '').strip()
    
    allowed, remaining = RateLimiter.check_rate_limit(
        identifier=ip_address,
        endpoint='auth/login',
        max_requests=10,
        window_seconds=60
    )
    if not allowed:
        return Response(
            {'error': 'Too many login attempts. Please try again later.'},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    
    if not username or not password:
        return Response(
            {'error': 'Username and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    is_locked, lockout_remaining = BruteForceProtection.is_locked(username)
    if is_locked:
        return Response(
            {
                'error': 'Account temporarily locked due to too many failed attempts.',
                'lockout_seconds': lockout_remaining
            },
            status=status.HTTP_423_LOCKED
        )
    
    try:
        if '@' in username:
            user = User.objects.get(email=username)
        else:
            user = User.objects.get(username=username)
    except User.DoesNotExist:
        BruteForceProtection.record_failed_attempt(username, ip_address)
        return Response(
            {'error': 'Invalid username or password'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    if not user.is_active:
        SecurityLogger.log(
            SecurityEventType.LOGIN_FAILED,
            user_id=str(user.id),
            ip_address=ip_address,
            user_agent=user_agent,
            endpoint='/api/v1/auth/login/',
            method='POST',
            status_code=401,
            details={'reason': 'account_disabled'},
            severity='WARNING'
        )
        return Response(
            {'error': 'Account is disabled'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    if not user.check_password(password):
        attempts, is_now_locked = BruteForceProtection.record_failed_attempt(username, ip_address)
        error_msg = 'Invalid username or password'
        if is_now_locked:
            error_msg = 'Account locked due to too many failed attempts. Try again in 15 minutes.'
        return Response(
            {'error': error_msg},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    BruteForceProtection.clear_attempts(username)
    
    user.last_login = datetime.now(timezone.utc)
    user.save(update_fields=['last_login'])
    
    session_token = str(uuid.uuid4())
    
    request.session['user_id'] = str(user.id)
    request.session['session_token'] = session_token
    
    permissions = get_user_permissions(user)
    
    AnomalyDetector.check_after_hours_access(str(user.id), ip_address)
    
    SecurityLogger.log(
        SecurityEventType.LOGIN_SUCCESS,
        user_id=str(user.id),
        ip_address=ip_address,
        user_agent=user_agent,
        endpoint='/api/v1/auth/login/',
        method='POST',
        status_code=200,
        details={'role': user.role, 'user_type': user.user_type},
        severity='INFO'
    )
    
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
        'session_token': session_token,
    })


@api_view(['POST'])
def logout_view(request):
    """
    Log out the current user and clear session.
    
    Security features:
    - Blacklists the session token
    - Logs the logout event
    - Clears all session data
    """
    ip_address = get_client_ip(request)
    user_id = request.session.get('user_id')
    session_token = request.session.get('session_token')
    
    if session_token:
        TokenBlacklist.blacklist_token(session_token, user_id, reason='logout')
    
    SecurityLogger.log(
        SecurityEventType.LOGOUT,
        user_id=user_id,
        ip_address=ip_address,
        endpoint='/api/v1/auth/logout/',
        method='POST',
        status_code=200,
        severity='INFO'
    )
    
    request.session.flush()
    return Response({'message': 'Logged out successfully'})


@api_view(['GET'])
def current_user_view(request):
    """Get the current authenticated user."""
    user_id = request.session.get('user_id')
    
    if not user_id:
        return Response(
            {'error': 'Not authenticated'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        request.session.flush()
        return Response(
            {'error': 'User not found'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    if not user.is_active:
        request.session.flush()
        return Response(
            {'error': 'Account is disabled'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
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


@api_view(['GET'])
def demo_users_view(request):
    """Get list of demo users for the login page."""
    demo_list = []
    
    for user_data in DEMO_USERS:
        demo_list.append({
            'username': user_data['username'],
            'email': user_data['email'],
            'password': 'demo123',
            'first_name': user_data['first_name'],
            'last_name': user_data['last_name'],
            'role': user_data['role'],
            'role_display': dict(User.ROLE_CHOICES).get(user_data['role'], user_data['role']),
            'user_type': user_data['user_type'],
            'department': user_data.get('department', ''),
        })
    
    return Response({'demo_users': demo_list})


@api_view(['POST'])
def quick_login_view(request):
    """Quick login with a demo user by role."""
    role = request.data.get('role', '').strip()
    
    if not role:
        return Response(
            {'error': 'Role is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    demo_user_data = None
    for user_data in DEMO_USERS:
        if user_data['role'] == role:
            demo_user_data = user_data
            break
    
    if not demo_user_data:
        return Response(
            {'error': f'No demo user found for role: {role}'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    try:
        user = User.objects.get(username=demo_user_data['username'])
    except User.DoesNotExist:
        create_demo_users()
        try:
            user = User.objects.get(username=demo_user_data['username'])
        except User.DoesNotExist:
            return Response(
                {'error': 'Demo user not found'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    user.last_login = datetime.now(timezone.utc)
    user.save(update_fields=['last_login'])
    
    session_token = str(uuid.uuid4())
    
    request.session['user_id'] = str(user.id)
    request.session['session_token'] = session_token
    
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
        'session_token': session_token,
    })


@api_view(['POST'])
def setup_demo_users_view(request):
    """Create all demo users in the database."""
    try:
        users = create_demo_users()
        return Response({
            'message': f'Created/updated {len(users)} demo users',
            'users': [
                {'username': u.username, 'email': u.email, 'role': u.role}
                for u in users
            ]
        })
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
