import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone
from rest_framework.test import APIClient
from unittest.mock import patch, MagicMock
import uuid


@pytest.fixture(scope='function')
def django_db_setup(django_db_blocker):
    pass


@pytest.fixture
def authenticated_api_client(db, create_user):
    client = APIClient()
    user = create_user(role='user')
    client.force_authenticate(user=user)
    client.user = user
    return client


@pytest.fixture
def admin_api_client(db, create_user):
    client = APIClient()
    user = create_user(role='admin', username=f'admin_client_{uuid.uuid4().hex[:8]}')
    client.force_authenticate(user=user)
    client.user = user
    return client


@pytest.fixture
def finance_api_client(db, create_user):
    client = APIClient()
    user = create_user(role='finance', username=f'finance_{uuid.uuid4().hex[:8]}')
    client.force_authenticate(user=user)
    client.user = user
    return client


@pytest.fixture
def hr_api_client(db, create_user):
    client = APIClient()
    user = create_user(role='hr', username=f'hr_{uuid.uuid4().hex[:8]}')
    client.force_authenticate(user=user)
    client.user = user
    return client


@pytest.fixture
def site_manager_api_client(db, create_user):
    client = APIClient()
    user = create_user(role='site_manager', username=f'site_mgr_{uuid.uuid4().hex[:8]}')
    client.force_authenticate(user=user)
    client.user = user
    return client


@pytest.fixture
def operations_api_client(db, create_user):
    client = APIClient()
    user = create_user(role='operations', username=f'ops_{uuid.uuid4().hex[:8]}')
    client.force_authenticate(user=user)
    client.user = user
    return client


@pytest.fixture
def unauthenticated_api_client():
    return APIClient()


@pytest.fixture
def mock_azure_ad_token():
    return {
        'oid': str(uuid.uuid4()),
        'preferred_username': 'testuser@company.com',
        'name': 'Test User',
        'roles': ['Finance_User'],
    }


@pytest.fixture
def user_data():
    unique_id = uuid.uuid4().hex[:8]
    return {
        'id': str(uuid.uuid4()),
        'username': f'testuser_{unique_id}',
        'email': f'testuser_{unique_id}@example.com',
        'first_name': 'Test',
        'last_name': 'User',
        'role': 'user',
        'department': 'Engineering',
        'is_active': True,
    }


@pytest.fixture
def admin_user_data():
    unique_id = uuid.uuid4().hex[:8]
    return {
        'id': str(uuid.uuid4()),
        'username': f'admin_{unique_id}',
        'email': f'admin_{unique_id}@example.com',
        'first_name': 'Admin',
        'last_name': 'User',
        'role': 'admin',
        'department': 'Management',
        'is_active': True,
    }


@pytest.fixture
def account_data():
    return {
        'id': str(uuid.uuid4()),
        'name': 'Test Company Pty Ltd',
        'legal_name': 'Test Company (Pty) Ltd',
        'industry': 'Construction',
        'type': 'customer',
        'status': 'active',
        'website': 'https://testcompany.co.za',
        'phone': '+27 11 123 4567',
        'email': 'info@testcompany.co.za',
        'account_number': 'ACC-001',
        'tax_id': '1234567890',
        'payment_terms': 'net_30',
        'credit_limit': Decimal('500000.00'),
        'currency': 'ZAR',
        'annual_revenue': Decimal('10000000.00'),
    }


@pytest.fixture
def contact_data():
    return {
        'id': str(uuid.uuid4()),
        'first_name': 'Thabo',
        'last_name': 'Molefe',
        'email': 'thabo.molefe@testcompany.co.za',
        'phone': '+27 11 123 4568',
        'mobile': '+27 82 123 4567',
        'title': 'Project Manager',
        'department': 'Operations',
        'is_primary': True,
        'preferred_communication': 'email',
        'status': 'active',
    }


@pytest.fixture
def project_data():
    return {
        'id': str(uuid.uuid4()),
        'name': 'Johannesburg Office Complex',
        'location': 'Sandton, Johannesburg',
        'status': 'active',
        'progress': 45,
        'budget': Decimal('15000000.00'),
        'due_date': '2024-12-31',
        'description': 'Multi-story office development in Sandton CBD',
    }


@pytest.fixture
def equipment_data():
    return {
        'id': str(uuid.uuid4()),
        'name': 'Caterpillar Excavator 320',
        'status': 'operational',
        'location': 'Site A - Sandton',
        'next_service': '2024-06-15',
        'serial_number': 'CAT320-2024-001',
        'purchase_price': Decimal('2500000.00'),
    }


@pytest.fixture
def product_data():
    return {
        'id': str(uuid.uuid4()),
        'sku': 'CEMENT-50KG-001',
        'name': 'Premium Cement 50kg',
        'description': 'High-quality Portland cement for construction',
        'category': 'Building Materials',
        'unit_price': Decimal('125.00'),
        'cost_price': Decimal('95.00'),
        'unit': 'bag',
        'reorder_level': 100,
        'reorder_quantity': 500,
        'is_active': True,
    }


@pytest.fixture
def warehouse_data():
    return {
        'id': str(uuid.uuid4()),
        'name': 'Johannesburg Central Warehouse',
        'code': 'JHB-CEN-01',
        'address': '123 Industrial Road',
        'city': 'Johannesburg',
        'country': 'South Africa',
        'capacity': 10000,
        'is_active': True,
    }


@pytest.fixture
def employee_data():
    return {
        'id': str(uuid.uuid4()),
        'employee_number': 'EMP-001',
        'first_name': 'Sipho',
        'last_name': 'Nkosi',
        'email': 'sipho.nkosi@constructos.co.za',
        'phone': '+27 82 555 1234',
        'department': 'Construction',
        'position': 'Site Supervisor',
        'hire_date': timezone.now() - timedelta(days=365),
        'salary': Decimal('45000.00'),
        'salary_frequency': 'monthly',
        'status': 'active',
        'city': 'Johannesburg',
        'country': 'South Africa',
    }


@pytest.fixture
def invoice_data():
    return {
        'id': str(uuid.uuid4()),
        'invoice_number': 'INV-2024-001',
        'status': 'draft',
        'due_date': timezone.now() + timedelta(days=30),
        'subtotal': Decimal('100000.00'),
        'tax_amount': Decimal('15000.00'),
        'total_amount': Decimal('115000.00'),
        'currency': 'ZAR',
    }


@pytest.fixture
def ticket_data():
    return {
        'id': str(uuid.uuid4()),
        'ticket_number': 'TKT-2024-001',
        'subject': 'Equipment maintenance required',
        'description': 'Scheduled maintenance for excavator',
        'status': 'open',
        'priority': 'medium',
        'type': 'maintenance',
        'source': 'internal',
    }


@pytest.fixture
def safety_inspection_data():
    return {
        'id': str(uuid.uuid4()),
        'site': 'Sandton Construction Site',
        'type': 'routine',
        'status': 'completed',
        'inspector': 'John Safety',
        'notes': 'All safety protocols followed',
        'findings': 'No major issues found',
        'corrective_actions': 'Minor signage improvements recommended',
    }


@pytest.fixture
def lead_data():
    return {
        'id': str(uuid.uuid4()),
        'first_name': 'Nomsa',
        'last_name': 'Dlamini',
        'email': 'nomsa.dlamini@prospect.co.za',
        'phone': '+27 11 987 6543',
        'company': 'Future Developments (Pty) Ltd',
        'title': 'CEO',
        'source': 'website',
        'status': 'new',
        'rating': 'hot',
        'estimated_value': Decimal('5000000.00'),
        'description': 'Interested in commercial construction project',
    }


@pytest.fixture
def opportunity_data():
    return {
        'id': str(uuid.uuid4()),
        'name': 'Cape Town Waterfront Project',
        'amount': Decimal('25000000.00'),
        'probability': 60,
        'close_date': timezone.now() + timedelta(days=90),
        'type': 'new_business',
        'source': 'referral',
        'description': 'Mixed-use development opportunity',
        'status': 'open',
    }


@pytest.fixture
def campaign_data():
    return {
        'id': str(uuid.uuid4()),
        'name': 'Q1 2024 Construction Expo',
        'type': 'trade_show',
        'status': 'active',
        'start_date': timezone.now(),
        'end_date': timezone.now() + timedelta(days=7),
        'budget': Decimal('150000.00'),
        'expected_revenue': Decimal('500000.00'),
        'description': 'Annual construction industry expo',
        'target_audience': 'Property developers and contractors',
    }


@pytest.fixture
def sla_data():
    return {
        'id': str(uuid.uuid4()),
        'name': 'Premium Support SLA',
        'description': 'Priority support for premium clients',
        'response_time_hours': 4,
        'resolution_time_hours': 24,
        'priority': 'high',
        'is_active': True,
    }


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, db):
    from backend.apps.core.models import User
    user = User.objects.create(
        id=str(uuid.uuid4()),
        username='testclient',
        email='testclient@example.com',
        role='admin',
        is_active=True,
    )
    return api_client


@pytest.fixture
def create_user(db):
    from backend.apps.core.models import User
    
    def _create_user(**kwargs):
        defaults = {
            'id': str(uuid.uuid4()),
            'username': f'user_{uuid.uuid4().hex[:8]}',
            'email': f'{uuid.uuid4().hex[:8]}@example.com',
            'role': 'user',
            'is_active': True,
        }
        defaults.update(kwargs)
        return User.objects.create(**defaults)
    
    return _create_user


@pytest.fixture
def create_account(db, create_user):
    from backend.apps.crm.models import Account
    
    def _create_account(**kwargs):
        defaults = {
            'id': str(uuid.uuid4()),
            'name': f'Account {uuid.uuid4().hex[:8]}',
            'type': 'customer',
            'status': 'active',
            'currency': 'ZAR',
        }
        defaults.update(kwargs)
        return Account.objects.create(**defaults)
    
    return _create_account


@pytest.fixture
def create_contact(db, create_account):
    from backend.apps.crm.models import Contact
    
    def _create_contact(account=None, **kwargs):
        if account is None:
            account = create_account()
        defaults = {
            'id': str(uuid.uuid4()),
            'first_name': 'Test',
            'last_name': 'Contact',
            'email': f'{uuid.uuid4().hex[:8]}@example.com',
            'account': account,
            'status': 'active',
        }
        defaults.update(kwargs)
        return Contact.objects.create(**defaults)
    
    return _create_contact


@pytest.fixture
def create_project(db, create_account, create_user):
    from backend.apps.construction.models import Project
    
    def _create_project(account=None, manager=None, **kwargs):
        defaults = {
            'id': str(uuid.uuid4()),
            'name': f'Project {uuid.uuid4().hex[:8]}',
            'location': 'Johannesburg',
            'status': 'active',
            'progress': 0,
            'budget': Decimal('1000000.00'),
            'due_date': '2024-12-31',
        }
        if account:
            defaults['account'] = account
        if manager:
            defaults['manager'] = manager
        defaults.update(kwargs)
        return Project.objects.create(**defaults)
    
    return _create_project


@pytest.fixture
def create_warehouse(db, create_user):
    from backend.apps.erp.models import Warehouse
    
    def _create_warehouse(**kwargs):
        defaults = {
            'id': str(uuid.uuid4()),
            'name': f'Warehouse {uuid.uuid4().hex[:8]}',
            'code': f'WH-{uuid.uuid4().hex[:6]}',
            'city': 'Johannesburg',
            'country': 'South Africa',
            'is_active': True,
        }
        defaults.update(kwargs)
        return Warehouse.objects.create(**defaults)
    
    return _create_warehouse


@pytest.fixture
def create_product(db):
    from backend.apps.erp.models import Product
    
    def _create_product(**kwargs):
        defaults = {
            'id': str(uuid.uuid4()),
            'sku': f'SKU-{uuid.uuid4().hex[:8]}',
            'name': f'Product {uuid.uuid4().hex[:8]}',
            'unit_price': Decimal('100.00'),
            'is_active': True,
        }
        defaults.update(kwargs)
        return Product.objects.create(**defaults)
    
    return _create_product


@pytest.fixture
def create_employee(db, create_user):
    from backend.apps.erp.models import Employee
    
    def _create_employee(user=None, **kwargs):
        defaults = {
            'id': str(uuid.uuid4()),
            'employee_number': f'EMP-{uuid.uuid4().hex[:6]}',
            'first_name': 'Test',
            'last_name': 'Employee',
            'email': f'{uuid.uuid4().hex[:8]}@example.com',
            'hire_date': timezone.now(),
            'status': 'active',
        }
        if user:
            defaults['user'] = user
        defaults.update(kwargs)
        return Employee.objects.create(**defaults)
    
    return _create_employee
