"""
Factory Boy factories for ConstructOS models.
Used for programmatic test data creation with proper RBAC attribute support.
"""

import factory
import uuid
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from factory.django import DjangoModelFactory

from backend.apps.core.models import User
from backend.apps.crm.models import Account, Contact, Lead, Opportunity, PipelineStage
from backend.apps.erp.models import (
    Warehouse, Product, StockItem, Invoice, InvoiceLineItem,
    Employee, PayrollRecord
)
from backend.apps.construction.models import Project, Transaction, Equipment, SafetyInspection


SITE_JHB = 'SIT-JHB-001'
SITE_CPT = 'SIT-CPT-002'
SITE_DBN = 'SIT-DBN-003'
SITE_PTA = 'SIT-PTA-004'
SITE_OTHER = 'SIT-OTHER-999'

WH_JHB = 'WH-JHB-001'
WH_CPT = 'WH-CPT-002'
WH_OTHER = 'WH-OTHER-999'


class UserFactory(DjangoModelFactory):
    """Factory for User model with RBAC role support."""
    
    class Meta:
        model = User
        django_get_or_create = ('username',)
    
    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    username = factory.Sequence(lambda n: f'user_{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@constructos.co.za')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    role = 'field_worker'
    department = 'Operations'
    user_type = 'internal'
    is_active = True
    
    @classmethod
    def create_system_admin(cls, **kwargs):
        return cls.create(role='system_admin', department='IT', **kwargs)
    
    @classmethod
    def create_executive(cls, **kwargs):
        return cls.create(role='executive', department='Executive', **kwargs)
    
    @classmethod
    def create_finance_manager(cls, **kwargs):
        return cls.create(role='finance_manager', department='Finance', **kwargs)
    
    @classmethod
    def create_hr_specialist(cls, **kwargs):
        return cls.create(role='hr_specialist', department='Human Resources', **kwargs)
    
    @classmethod
    def create_sales_rep(cls, **kwargs):
        return cls.create(role='sales_rep', department='Sales', **kwargs)
    
    @classmethod
    def create_operations_specialist(cls, **kwargs):
        return cls.create(role='operations_specialist', department='Operations', **kwargs)
    
    @classmethod
    def create_site_manager(cls, site_id=SITE_JHB, **kwargs):
        return cls.create(role='site_manager', department='Operations', **kwargs)
    
    @classmethod
    def create_field_worker(cls, site_id=SITE_JHB, **kwargs):
        return cls.create(role='field_worker', department='Operations', **kwargs)
    
    @classmethod
    def create_warehouse_clerk(cls, warehouse_id=WH_JHB, **kwargs):
        return cls.create(role='warehouse_clerk', department='Logistics', **kwargs)
    
    @classmethod
    def create_subcontractor(cls, **kwargs):
        return cls.create(role='subcontractor', department='External', user_type='external', **kwargs)
    
    @classmethod
    def create_client(cls, **kwargs):
        return cls.create(role='client', department='External', user_type='external', **kwargs)


class AccountFactory(DjangoModelFactory):
    """Factory for Account model."""
    
    class Meta:
        model = Account
        django_get_or_create = ('account_number',)
    
    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f'Test Company {n}')
    account_number = factory.Sequence(lambda n: f'ACC-TEST-{n:05d}')
    type = 'customer'
    industry = 'Construction'
    status = 'active'
    currency = 'ZAR'
    tier = 'Mid-Market'
    owner = factory.SubFactory(UserFactory)


class ContactFactory(DjangoModelFactory):
    """Factory for Contact model."""
    
    class Meta:
        model = Contact
    
    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.LazyAttribute(lambda obj: f'{obj.first_name.lower()}.{obj.last_name.lower()}@test.co.za')
    account = factory.SubFactory(AccountFactory)
    status = 'active'
    is_primary = True


class PipelineStageFactory(DjangoModelFactory):
    """Factory for PipelineStage model."""
    
    class Meta:
        model = PipelineStage
        django_get_or_create = ('name',)
    
    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f'Stage {n}')
    order = factory.Sequence(lambda n: n)
    probability = 50
    color = '#3B82F6'


class LeadFactory(DjangoModelFactory):
    """Factory for Lead model with ownership support."""
    
    class Meta:
        model = Lead
    
    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.LazyAttribute(lambda obj: f'{obj.first_name.lower()}.{obj.last_name.lower()}@prospect.co.za')
    company = factory.Sequence(lambda n: f'Prospect Company {n}')
    title = 'Director'
    source = 'Website Form'
    status = 'qualified'
    rating = 'Hot'
    estimated_value = Decimal('1000000')
    owner = factory.SubFactory(UserFactory, role='sales_rep')


class OpportunityFactory(DjangoModelFactory):
    """Factory for Opportunity model with ownership support."""
    
    class Meta:
        model = Opportunity
    
    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f'Opportunity {n}')
    account = factory.SubFactory(AccountFactory)
    stage = factory.SubFactory(PipelineStageFactory)
    amount = Decimal('5000000')
    probability = 50
    close_date = factory.LazyFunction(lambda: timezone.now() + timedelta(days=90))
    type = 'New Business'
    source = 'Referral'
    status = 'open'
    owner = factory.SubFactory(UserFactory, role='sales_rep')


class WarehouseFactory(DjangoModelFactory):
    """Factory for Warehouse model with location support."""
    
    class Meta:
        model = Warehouse
        django_get_or_create = ('code',)
    
    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f'Warehouse {n}')
    code = factory.Sequence(lambda n: f'WH-TEST-{n:03d}')
    address = '123 Industrial Road'
    city = 'Johannesburg'
    country = 'South Africa'
    capacity = 10000
    is_active = True


class ProductFactory(DjangoModelFactory):
    """Factory for Product model."""
    
    class Meta:
        model = Product
        django_get_or_create = ('sku',)
    
    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    sku = factory.Sequence(lambda n: f'PROD-TEST-{n:05d}')
    name = factory.Sequence(lambda n: f'Test Product {n}')
    description = 'Test product for RBAC testing'
    category = 'Construction Materials'
    unit = 'each'
    unit_price = Decimal('100.00')
    cost_price = Decimal('60.00')
    reorder_level = 10
    reorder_quantity = 50
    is_active = True


class StockItemFactory(DjangoModelFactory):
    """Factory for StockItem model with warehouse location."""
    
    class Meta:
        model = StockItem
    
    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    product = factory.SubFactory(ProductFactory)
    warehouse = factory.SubFactory(WarehouseFactory)
    quantity = 100
    reserved_quantity = 10
    available_quantity = 90
    location = 'Aisle 1'


class EmployeeFactory(DjangoModelFactory):
    """Factory for Employee model with sensitive data support."""
    
    class Meta:
        model = Employee
    
    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    employee_number = factory.Sequence(lambda n: f'EMP-TEST-{n:05d}')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.LazyAttribute(lambda obj: f'{obj.first_name.lower()}.{obj.last_name.lower()}@constructos.co.za')
    phone = '+27 11 123 4567'
    department = 'Operations'
    position = 'Worker'
    salary = Decimal('500000')
    salary_frequency = 'monthly'
    hire_date = factory.LazyFunction(lambda: timezone.now() - timedelta(days=365))
    status = 'active'
    city = 'Johannesburg'
    country = 'South Africa'
    
    @classmethod
    def create_with_sensitive_data(cls, **kwargs):
        """Create employee with sensitive banking details."""
        return cls.create(**kwargs)


class PayrollRecordFactory(DjangoModelFactory):
    """Factory for PayrollRecord model."""
    
    class Meta:
        model = PayrollRecord
    
    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    employee = factory.SubFactory(EmployeeFactory)
    period_start = factory.LazyFunction(lambda: timezone.now().replace(day=1) - timedelta(days=30))
    period_end = factory.LazyFunction(lambda: timezone.now().replace(day=1) - timedelta(days=1))
    base_salary = Decimal('41666.67')
    overtime = Decimal('0')
    bonus = Decimal('0')
    deductions = Decimal('10416.67')
    tax_amount = Decimal('8333.33')
    net_pay = Decimal('22916.67')
    status = 'draft'


class InvoiceFactory(DjangoModelFactory):
    """Factory for Invoice model with status support."""
    
    class Meta:
        model = Invoice
        django_get_or_create = ('invoice_number',)
    
    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    invoice_number = factory.Sequence(lambda n: f'INV-TEST-{n:05d}')
    account = factory.SubFactory(AccountFactory)
    status = 'draft'
    due_date = factory.LazyFunction(lambda: timezone.now() + timedelta(days=30))
    subtotal = Decimal('100000')
    tax_amount = Decimal('15000')
    total_amount = Decimal('115000')
    paid_amount = Decimal('0')
    
    @classmethod
    def create_pending(cls, **kwargs):
        """Create invoice pending approval."""
        return cls.create(status='draft', **kwargs)
    
    @classmethod
    def create_approved(cls, **kwargs):
        """Create approved/paid invoice."""
        defaults = {
            'status': 'paid',
            'paid_amount': Decimal('115000'),
        }
        defaults.update(kwargs)
        return cls.create(**defaults)


class ProjectFactory(DjangoModelFactory):
    """Factory for Project model with site/geographic scope support."""
    
    class Meta:
        model = Project
    
    id = factory.Sequence(lambda n: f'PRJ-TEST-{n:03d}')
    name = factory.Sequence(lambda n: f'Test Project {n}')
    location = 'Johannesburg'
    status = 'In Progress'
    progress = 50
    budget = Decimal('10000000')
    due_date = factory.LazyFunction(lambda: (timezone.now() + timedelta(days=365)).strftime('%Y-%m-%d'))
    description = 'Test project for RBAC testing'
    account = factory.SubFactory(AccountFactory)
    manager = factory.SubFactory(UserFactory, role='site_manager')
    start_date = factory.LazyFunction(timezone.now)
    
    @classmethod
    def create_for_site(cls, site_id, manager=None, **kwargs):
        """Create project linked to a specific site."""
        location_map = {
            SITE_JHB: 'Johannesburg',
            SITE_CPT: 'Cape Town',
            SITE_DBN: 'Durban',
            SITE_PTA: 'Pretoria',
        }
        defaults = {
            'location': location_map.get(site_id, 'Unknown'),
        }
        if manager:
            defaults['manager'] = manager
        defaults.update(kwargs)
        return cls.create(**defaults)


class EquipmentFactory(DjangoModelFactory):
    """Factory for Equipment model."""
    
    class Meta:
        model = Equipment
    
    id = factory.Sequence(lambda n: f'EQ-TEST-{n:03d}')
    name = factory.Sequence(lambda n: f'Equipment {n}')
    status = 'Active'
    serial_number = factory.Sequence(lambda n: f'SN-TEST-{n:06d}')
    purchase_price = Decimal('100000')
    location = 'Johannesburg Site'
    warehouse = factory.SubFactory(WarehouseFactory)
    next_service = factory.LazyFunction(lambda: (timezone.now() + timedelta(days=30)).strftime('%Y-%m-%d'))
    purchase_date = factory.LazyFunction(lambda: timezone.now() - timedelta(days=180))


class SafetyInspectionFactory(DjangoModelFactory):
    """Factory for SafetyInspection model."""
    
    class Meta:
        model = SafetyInspection
    
    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    project = factory.SubFactory(ProjectFactory)
    type = 'Daily Walkthrough'
    status = 'completed'
    inspector = 'Safety Inspector'
    notes = 'Routine inspection completed'
    findings = 'All safety protocols followed'
    corrective_actions = 'None required'


class TransactionFactory(DjangoModelFactory):
    """Factory for Transaction model."""
    
    class Meta:
        model = Transaction
    
    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    project = factory.SubFactory(ProjectFactory)
    description = 'Test transaction'
    amount = Decimal('50000')
    status = 'approved'
    category = 'Materials'
    type = 'expense'
