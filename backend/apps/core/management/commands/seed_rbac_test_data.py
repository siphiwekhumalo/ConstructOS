"""
Django management command to seed RBAC test data for ConstructOS.
This generates specific data for testing role-based permissions across all 11 user roles.

Test Scenarios Covered:
1. System Admin / Executive Viewer - Full vs Read-only access
2. Finance Manager / HR Specialist - Segregation of Duties (SoD)
3. Sales Representative - Ownership-based access
4. Site Manager / Field Worker - Geographic/Project scope
5. Warehouse Clerk - Location-specific access
6. Subcontractor / Client - External user access
"""

import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.hashers import make_password

from backend.apps.core.models import User
from backend.apps.crm.models import (
    Account, Contact, Address, PipelineStage, Lead, Opportunity,
    Ticket, Sla
)
from backend.apps.erp.models import (
    Warehouse, Product, StockItem, Invoice, InvoiceLineItem, Payment,
    Employee, PayrollRecord
)
from backend.apps.construction.models import (
    Project, Transaction, Equipment, SafetyInspection, Document
)


SITE_IDS = ['SIT-JHB-001', 'SIT-CPT-002', 'SIT-DBN-003', 'SIT-PTA-004', 'SIT-PE-005']
WAREHOUSE_LOCATION_IDS = ['WH-JHB-MAIN', 'WH-CPT-DOCK', 'WH-DBN-HARBOR']

DEMO_PASSWORD = make_password('demo123')


class Command(BaseCommand):
    help = 'Seed database with comprehensive RBAC test data for all 11 user roles'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing RBAC test data before seeding',
        )

    def handle(self, *args, **options):
        self.stdout.write('Starting RBAC test data seed...')
        
        with transaction.atomic():
            users = self.create_rbac_users()
            sites = self.create_sites_and_warehouses()
            self.create_rbac_accounts(users)
            self.create_leads_opportunities(users)
            self.create_invoices_with_statuses(users)
            self.create_hr_data(users)
            self.create_project_data(users, sites)
            self.create_inventory_data(users, sites)
        
        self.print_summary()
        self.stdout.write(self.style.SUCCESS('RBAC test data seeded successfully!'))

    def print_summary(self):
        self.stdout.write('\n=== RBAC TEST DATA SUMMARY ===')
        self.stdout.write(f'Users: {User.objects.count()}')
        self.stdout.write(f'  - System Admins: {User.objects.filter(role="system_admin").count()}')
        self.stdout.write(f'  - Executives: {User.objects.filter(role="executive").count()}')
        self.stdout.write(f'  - Finance Managers: {User.objects.filter(role="finance_manager").count()}')
        self.stdout.write(f'  - HR Specialists: {User.objects.filter(role="hr_specialist").count()}')
        self.stdout.write(f'  - Sales Reps: {User.objects.filter(role="sales_rep").count()}')
        self.stdout.write(f'  - Site Managers: {User.objects.filter(role="site_manager").count()}')
        self.stdout.write(f'  - Field Workers: {User.objects.filter(role="field_worker").count()}')
        self.stdout.write(f'  - Warehouse Clerks: {User.objects.filter(role="warehouse_clerk").count()}')
        self.stdout.write(f'  - Subcontractors: {User.objects.filter(role="subcontractor").count()}')
        self.stdout.write(f'  - Clients: {User.objects.filter(role="client").count()}')
        self.stdout.write(f'Leads: {Lead.objects.count()}')
        self.stdout.write(f'Opportunities: {Opportunity.objects.count()}')
        self.stdout.write(f'Invoices: {Invoice.objects.count()}')
        self.stdout.write(f'Projects: {Project.objects.count()}')
        self.stdout.write(f'Employees: {Employee.objects.count()}')
        self.stdout.write(f'Warehouses: {Warehouse.objects.count()}')
        self.stdout.write('================================')

    def create_rbac_users(self):
        """Create users for each role with specific IDs for testing."""
        self.stdout.write('Creating RBAC test users...')
        
        rbac_users = [
            {
                'id': 'usr-admin-001',
                'username': 'admin_user',
                'email': 'admin@constructos.co.za',
                'first_name': 'System',
                'last_name': 'Administrator',
                'role': 'system_admin',
                'department': 'IT',
                'user_type': 'internal',
            },
            {
                'id': 'usr-exec-001',
                'username': 'exec_user',
                'email': 'exec@constructos.co.za',
                'first_name': 'Executive',
                'last_name': 'Viewer',
                'role': 'executive',
                'department': 'Executive',
                'user_type': 'internal',
            },
            {
                'id': 'usr-finance-001',
                'username': 'finance_mgr',
                'email': 'finance.manager@constructos.co.za',
                'first_name': 'Lindiwe',
                'last_name': 'Finance',
                'role': 'finance_manager',
                'department': 'Finance',
                'user_type': 'internal',
            },
            {
                'id': 'usr-hr-001',
                'username': 'hr_specialist',
                'email': 'hr.specialist@constructos.co.za',
                'first_name': 'Annemarie',
                'last_name': 'Human',
                'role': 'hr_specialist',
                'department': 'Human Resources',
                'user_type': 'internal',
            },
            {
                'id': 'usr-sales-101',
                'username': 'sales_rep_101',
                'email': 'sales101@constructos.co.za',
                'first_name': 'Thabo',
                'last_name': 'Sales',
                'role': 'sales_rep',
                'department': 'Sales',
                'user_type': 'internal',
            },
            {
                'id': 'usr-sales-102',
                'username': 'sales_rep_102',
                'email': 'sales102@constructos.co.za',
                'first_name': 'Nomvula',
                'last_name': 'Seller',
                'role': 'sales_rep',
                'department': 'Sales',
                'user_type': 'internal',
            },
            {
                'id': 'usr-ops-001',
                'username': 'ops_specialist',
                'email': 'ops@constructos.co.za',
                'first_name': 'Pieter',
                'last_name': 'Operations',
                'role': 'operations_specialist',
                'department': 'Operations',
                'user_type': 'internal',
            },
            {
                'id': 'usr-site-001',
                'username': 'site_mgr_pta',
                'email': 'site.pta@constructos.co.za',
                'first_name': 'Johan',
                'last_name': 'SiteManager',
                'role': 'site_manager',
                'department': 'Operations',
                'user_type': 'internal',
                'assigned_site_id': 'SIT-PTA-004',
            },
            {
                'id': 'usr-site-002',
                'username': 'site_mgr_jhb',
                'email': 'site.jhb@constructos.co.za',
                'first_name': 'Bongani',
                'last_name': 'Builder',
                'role': 'site_manager',
                'department': 'Operations',
                'user_type': 'internal',
                'assigned_site_id': 'SIT-JHB-001',
            },
            {
                'id': 'usr-field-001',
                'username': 'field_worker_1',
                'email': 'field1@constructos.co.za',
                'first_name': 'Sipho',
                'last_name': 'FieldWork',
                'role': 'field_worker',
                'department': 'Operations',
                'user_type': 'internal',
                'assigned_site_id': 'SIT-PTA-004',
            },
            {
                'id': 'usr-field-002',
                'username': 'field_worker_2',
                'email': 'field2@constructos.co.za',
                'first_name': 'Andile',
                'last_name': 'Worker',
                'role': 'field_worker',
                'department': 'Operations',
                'user_type': 'internal',
                'assigned_site_id': 'SIT-JHB-001',
            },
            {
                'id': 'usr-wh-001',
                'username': 'wh_clerk_jhb',
                'email': 'wh.jhb@constructos.co.za',
                'first_name': 'David',
                'last_name': 'Warehouse',
                'role': 'warehouse_clerk',
                'department': 'Logistics',
                'user_type': 'internal',
                'assigned_warehouse_id': 'WH-JHB-MAIN',
            },
            {
                'id': 'usr-wh-002',
                'username': 'wh_clerk_cpt',
                'email': 'wh.cpt@constructos.co.za',
                'first_name': 'Lerato',
                'last_name': 'Stock',
                'role': 'warehouse_clerk',
                'department': 'Logistics',
                'user_type': 'internal',
                'assigned_warehouse_id': 'WH-CPT-DOCK',
            },
            {
                'id': 'usr-sub-001',
                'username': 'subcontractor_1',
                'email': 'subcontractor1@external.co.za',
                'first_name': 'Electrical',
                'last_name': 'Contractor',
                'role': 'subcontractor',
                'department': 'External',
                'user_type': 'external',
            },
            {
                'id': 'usr-sub-002',
                'username': 'subcontractor_2',
                'email': 'subcontractor2@external.co.za',
                'first_name': 'Plumbing',
                'last_name': 'Services',
                'role': 'subcontractor',
                'department': 'External',
                'user_type': 'external',
            },
            {
                'id': 'usr-client-001',
                'username': 'client_user_1',
                'email': 'client1@customer.co.za',
                'first_name': 'Property',
                'last_name': 'Developer',
                'role': 'client',
                'department': 'External',
                'user_type': 'external',
            },
            {
                'id': 'usr-client-002',
                'username': 'client_user_2',
                'email': 'client2@customer.co.za',
                'first_name': 'Commercial',
                'last_name': 'Builder',
                'role': 'client',
                'department': 'External',
                'user_type': 'external',
            },
        ]
        
        users = {}
        for user_data in rbac_users:
            user_id = user_data.pop('id')
            assigned_site_id = user_data.pop('assigned_site_id', None)
            assigned_warehouse_id = user_data.pop('assigned_warehouse_id', None)
            
            existing_user = User.objects.filter(
                username=user_data['username']
            ).first() or User.objects.filter(
                email=user_data['email']
            ).first()
            
            if existing_user:
                for key, value in user_data.items():
                    setattr(existing_user, key, value)
                existing_user.save()
                user = existing_user
                created = False
            else:
                user = User.objects.create(
                    id=user_id,
                    **user_data
                )
                user.set_password('demo123')
                user.save()
                created = True
            
            users[user_data['username']] = user
            action = 'Created' if created else 'Updated'
            self.stdout.write(f'  {action} user: {user.username} ({user.role})')
        
        return users

    def create_sites_and_warehouses(self):
        """Create sites and warehouses for geographic scoping tests."""
        self.stdout.write('Creating sites and warehouses...')
        
        warehouses_data = [
            {
                'id': 'WH-JHB-MAIN',
                'name': 'Johannesburg Main Distribution Centre',
                'code': 'WH-JHB',
                'address': '150 Industrial Road, Isando',
                'city': 'Johannesburg',
                'country': 'South Africa',
                'capacity': 50000,
            },
            {
                'id': 'WH-CPT-DOCK',
                'name': 'Cape Town Dockside Facility',
                'code': 'WH-CPT',
                'address': '28 Paarden Eiland Road',
                'city': 'Cape Town',
                'country': 'South Africa',
                'capacity': 35000,
            },
            {
                'id': 'WH-DBN-HARBOR',
                'name': 'Durban Harbour Depot',
                'code': 'WH-DBN',
                'address': '45 Maydon Wharf Road',
                'city': 'Durban',
                'country': 'South Africa',
                'capacity': 25000,
            },
        ]
        
        warehouses = {}
        for wh_data in warehouses_data:
            wh_id = wh_data.pop('id')
            existing = Warehouse.objects.filter(code=wh_data['code']).first()
            if existing:
                for key, value in wh_data.items():
                    setattr(existing, key, value)
                existing.save()
                warehouse = existing
            else:
                warehouse = Warehouse.objects.create(id=wh_id, **wh_data)
            warehouses[wh_id] = warehouse
        
        return {'warehouses': warehouses, 'site_ids': SITE_IDS}

    def create_rbac_accounts(self, users):
        """Create accounts with specific ownership for testing."""
        self.stdout.write('Creating accounts with ownership assignments...')
        
        accounts_data = [
            {
                'id': 'acc-client-001',
                'name': 'Property Developer Holdings',
                'type': 'customer',
                'industry': 'Real Estate Development',
                'tier': 'Enterprise',
                'owner': users.get('client_user_1'),
            },
            {
                'id': 'acc-client-002',
                'name': 'Commercial Builders Ltd',
                'type': 'customer',
                'industry': 'Commercial Construction',
                'tier': 'Strategic',
                'owner': users.get('client_user_2'),
            },
            {
                'id': 'acc-sub-001',
                'name': 'Electrical Contractors SA',
                'type': 'vendor',
                'industry': 'Electrical Services',
                'tier': 'Preferred',
                'owner': users.get('subcontractor_1'),
            },
            {
                'id': 'acc-sub-002',
                'name': 'Plumbing Services Pty',
                'type': 'vendor',
                'industry': 'Plumbing Services',
                'tier': 'Standard',
                'owner': users.get('subcontractor_2'),
            },
        ]
        
        for i in range(6):
            accounts_data.append({
                'id': f'acc-general-{i+1:03d}',
                'name': f'General Account {i+1}',
                'type': 'customer',
                'industry': 'Construction',
                'tier': 'Mid-Market',
                'owner': users.get('admin_user'),
            })
        
        accounts = {}
        for acc_data in accounts_data:
            acc_id = acc_data.pop('id')
            account_number = f"ACC-RBAC-{acc_id[-3:]}"
            
            existing = (
                Account.objects.filter(name=acc_data['name']).first() or
                Account.objects.filter(account_number=account_number).first()
            )
            if existing:
                for key, value in acc_data.items():
                    setattr(existing, key, value)
                existing.save()
                account = existing
            else:
                account = Account.objects.create(
                    id=acc_id,
                    account_number=account_number,
                    status='active',
                    currency='ZAR',
                    **acc_data
                )
            accounts[acc_id] = account
        
        return accounts

    def create_leads_opportunities(self, users):
        """Create leads and opportunities with specific ownership for Sales Rep testing."""
        self.stdout.write('Creating leads and opportunities with ownership...')
        
        stages = list(PipelineStage.objects.all())
        if not stages:
            stages = []
            for i, stage_data in enumerate([
                ('Qualification', 10), ('Proposal', 25), ('Negotiation', 50),
                ('Contract Review', 75), ('Closed Won', 100), ('Closed Lost', 0)
            ]):
                stage, _ = PipelineStage.objects.get_or_create(
                    name=stage_data[0],
                    defaults={'order': i+1, 'probability': stage_data[1], 'color': '#3B82F6'}
                )
                stages.append(stage)
        
        sales_rep_101 = users.get('sales_rep_101')
        sales_rep_102 = users.get('sales_rep_102')
        
        leads = []
        for i in range(10):
            owner = sales_rep_101 if i < 5 else sales_rep_102
            lead, _ = Lead.objects.update_or_create(
                email=f'lead{i+1}@prospect.co.za',
                defaults={
                    'id': f'lead-{i+1:03d}',
                    'first_name': f'Lead{i+1}',
                    'last_name': 'Prospect',
                    'company': f'Prospect Company {i+1}',
                    'title': 'Director',
                    'source': 'Website Form',
                    'status': 'qualified',
                    'rating': 'Hot' if i < 3 else 'Warm',
                    'estimated_value': Decimal('1000000') * (i+1),
                    'owner': owner,
                }
            )
            leads.append(lead)
            self.stdout.write(f'  Lead {i+1} assigned to {owner.username}')
        
        accounts = list(Account.objects.filter(type='customer')[:5])
        opps = []
        for i in range(10):
            owner = sales_rep_101 if i < 5 else sales_rep_102
            account = accounts[i % len(accounts)] if accounts else None
            opp, _ = Opportunity.objects.update_or_create(
                name=f'Opportunity Project {i+1}',
                defaults={
                    'id': f'opp-{i+1:03d}',
                    'account': account,
                    'stage': stages[i % 4] if stages else None,
                    'amount': Decimal('5000000') * (i+1),
                    'probability': 25 * ((i % 4) + 1),
                    'close_date': timezone.now() + timedelta(days=30 * (i+1)),
                    'type': 'New Business',
                    'source': 'Referral',
                    'status': 'open',
                    'owner': owner,
                }
            )
            opps.append(opp)
            self.stdout.write(f'  Opportunity {i+1} assigned to {owner.username}')
        
        return {'leads': leads, 'opportunities': opps}

    def create_invoices_with_statuses(self, users):
        """Create invoices with different statuses for Finance Manager testing."""
        self.stdout.write('Creating invoices with various statuses...')
        
        accounts = list(Account.objects.filter(type='customer')[:4])
        if not accounts:
            self.stdout.write('  No customer accounts found, skipping invoices')
            return []
        
        statuses = ['approved', 'approved', 'approved', 'approved', 'approved',
                    'pending', 'pending', 'pending', 'pending', 'pending']
        
        invoices = []
        for i, status in enumerate(statuses):
            account = accounts[i % len(accounts)]
            subtotal = Decimal('50000') * (i+1)
            tax = subtotal * Decimal('0.15')
            total = subtotal + tax
            
            invoice_number = f'INV-RBAC-{i+1:04d}'
            existing = Invoice.objects.filter(invoice_number=invoice_number).first()
            if existing:
                existing.status = 'paid' if status == 'approved' else 'draft'
                existing.account = account
                existing.save()
                invoice = existing
            else:
                invoice = Invoice.objects.create(
                    id=f'inv-rbac-{i+1:03d}',
                    invoice_number=invoice_number,
                    account=account,
                    status='paid' if status == 'approved' else 'draft',
                    due_date=timezone.now() + timedelta(days=30),
                    subtotal=subtotal,
                    tax_amount=tax,
                    total_amount=total,
                    paid_amount=total if status == 'approved' else Decimal('0'),
                    notes=f'RBAC Test Invoice - Status: {status}',
                )
            invoices.append(invoice)
            self.stdout.write(f'  Invoice {invoice.invoice_number}: {status}')
        
        return invoices

    def create_hr_data(self, users):
        """Create HR records with sensitive data for HR Specialist testing."""
        self.stdout.write('Creating HR data with sensitive records...')
        
        employees_data = [
            {
                'first_name': 'Thabo',
                'last_name': 'Molefe',
                'department': 'Operations',
                'position': 'Site Superintendent',
                'salary': Decimal('850000'),
                'bank_account': '123456789',
                'bank_name': 'FNB',
                'is_sensitive': True,
            },
            {
                'first_name': 'Lindiwe',
                'last_name': 'Pretorius',
                'department': 'Finance',
                'position': 'Controller',
                'salary': Decimal('1150000'),
                'bank_account': '987654321',
                'bank_name': 'Standard Bank',
                'is_sensitive': True,
            },
            {
                'first_name': 'Johan',
                'last_name': 'Van der Merwe',
                'department': 'Operations',
                'position': 'Project Engineer',
                'salary': Decimal('720000'),
                'bank_account': '456789123',
                'bank_name': 'ABSA',
                'is_sensitive': True,
            },
            {
                'first_name': 'Nomvula',
                'last_name': 'Khumalo',
                'department': 'Safety',
                'position': 'Safety Manager',
                'salary': Decimal('780000'),
                'bank_account': '789123456',
                'bank_name': 'Nedbank',
                'is_sensitive': True,
            },
            {
                'first_name': 'Sipho',
                'last_name': 'Dlamini',
                'department': 'Operations',
                'position': 'Equipment Operator',
                'salary': Decimal('420000'),
                'bank_account': '321654987',
                'bank_name': 'FNB',
                'is_sensitive': True,
            },
        ]
        
        employees = []
        for i, emp_data in enumerate(employees_data):
            bank_account = emp_data.pop('bank_account', None)
            bank_name = emp_data.pop('bank_name', None)
            is_sensitive = emp_data.pop('is_sensitive', False)
            
            emp, _ = Employee.objects.update_or_create(
                employee_number=f'EMP-RBAC-{i+1:04d}',
                defaults={
                    'id': f'emp-rbac-{i+1:03d}',
                    'email': f'{emp_data["first_name"].lower()}.{emp_data["last_name"].lower()}@constructos.co.za',
                    'phone': f'+27 11 {100+i:03d} {1000+i:04d}',
                    'hire_date': timezone.now() - timedelta(days=365 * (i+1)),
                    'status': 'active',
                    'salary_frequency': 'monthly',
                    'address': f'{100+i} Main Road',
                    'city': 'Johannesburg',
                    'country': 'South Africa',
                    **emp_data
                }
            )
            employees.append(emp)
            
            period_start = timezone.now().replace(day=1) - timedelta(days=30)
            existing_payroll = PayrollRecord.objects.filter(employee=emp, period_start=period_start).first()
            if not existing_payroll:
                PayrollRecord.objects.create(
                    id=f'pay-rbac-{i+1:03d}',
                    employee=emp,
                    period_start=period_start,
                    period_end=timezone.now().replace(day=1) - timedelta(days=1),
                    base_salary=emp_data['salary'] / 12,
                    overtime=Decimal('0'),
                    bonus=Decimal('0'),
                    deductions=emp_data['salary'] / 12 * Decimal('0.25'),
                    tax_amount=emp_data['salary'] / 12 * Decimal('0.20'),
                    net_pay=emp_data['salary'] / 12 * Decimal('0.55'),
                    status='draft' if i < 2 else 'processed',
                )
            self.stdout.write(f'  Employee: {emp.first_name} {emp.last_name} (sensitive={is_sensitive})')
        
        return employees

    def create_project_data(self, users, sites):
        """Create projects linked to different sites for Site Manager testing."""
        self.stdout.write('Creating projects linked to sites...')
        
        site_manager_pta = users.get('site_mgr_pta')
        site_manager_jhb = users.get('site_mgr_jhb')
        field_worker_1 = users.get('field_worker_1')
        field_worker_2 = users.get('field_worker_2')
        client_1 = users.get('client_user_1')
        client_2 = users.get('client_user_2')
        
        accounts = list(Account.objects.filter(type='customer')[:2])
        
        projects_data = [
            {
                'id': 'PRJ-JHB-001',
                'name': 'Johannesburg Office Tower',
                'site_id': 'SIT-JHB-001',
                'manager': site_manager_jhb,
                'location': 'Sandton, Johannesburg',
                'status': 'In Progress',
                'progress': 45,
                'budget': Decimal('250000000'),
            },
            {
                'id': 'PRJ-JHB-002',
                'name': 'Sandton Retail Centre',
                'site_id': 'SIT-JHB-001',
                'manager': site_manager_jhb,
                'location': 'Sandton CBD, Johannesburg',
                'status': 'In Progress',
                'progress': 65,
                'budget': Decimal('180000000'),
            },
            {
                'id': 'PRJ-PTA-001',
                'name': 'Pretoria Medical Centre',
                'site_id': 'SIT-PTA-004',
                'manager': site_manager_pta,
                'location': 'Centurion, Pretoria',
                'status': 'In Progress',
                'progress': 30,
                'budget': Decimal('320000000'),
            },
            {
                'id': 'PRJ-PTA-002',
                'name': 'Pretoria Government Complex',
                'site_id': 'SIT-PTA-004',
                'manager': site_manager_pta,
                'location': 'Arcadia, Pretoria',
                'status': 'Planning',
                'progress': 10,
                'budget': Decimal('450000000'),
            },
            {
                'id': 'PRJ-CPT-001',
                'name': 'Cape Town Waterfront Hotel',
                'site_id': 'SIT-CPT-002',
                'manager': site_manager_pta,
                'location': 'V&A Waterfront, Cape Town',
                'status': 'In Progress',
                'progress': 55,
                'budget': Decimal('280000000'),
            },
            {
                'id': 'PRJ-DBN-001',
                'name': 'Durban Logistics Hub',
                'site_id': 'SIT-DBN-003',
                'manager': None,
                'location': 'Maydon Wharf, Durban',
                'status': 'In Progress',
                'progress': 70,
                'budget': Decimal('120000000'),
            },
            {
                'id': 'PRJ-PE-001',
                'name': 'Port Elizabeth Industrial Park',
                'site_id': 'SIT-PE-005',
                'manager': None,
                'location': 'Coega, Port Elizabeth',
                'status': 'On Hold',
                'progress': 20,
                'budget': Decimal('95000000'),
            },
        ]
        
        projects = []
        for i, proj_data in enumerate(projects_data):
            site_id = proj_data.pop('site_id')
            proj_id = proj_data.pop('id')
            account = accounts[i % len(accounts)] if accounts else None
            
            project, _ = Project.objects.update_or_create(
                id=proj_id,
                defaults={
                    'account': account,
                    'start_date': timezone.now() - timedelta(days=90),
                    'due_date': (timezone.now() + timedelta(days=365)).strftime('%Y-%m-%d'),
                    'description': f'RBAC test project at site {site_id}',
                    **proj_data
                }
            )
            projects.append(project)
            self.stdout.write(f'  Project {proj_id}: {proj_data["name"]} (Site: {site_id})')
        
        return projects

    def create_inventory_data(self, users, sites):
        """Create inventory data for Warehouse Clerk location-specific testing."""
        self.stdout.write('Creating inventory with warehouse assignments...')
        
        warehouses = sites.get('warehouses', {})
        
        products = []
        for i in range(20):
            product, _ = Product.objects.update_or_create(
                sku=f'RBAC-PROD-{i+1:04d}',
                defaults={
                    'id': f'prod-rbac-{i+1:03d}',
                    'name': f'Construction Material {i+1}',
                    'description': f'Test product {i+1} for RBAC testing',
                    'category': 'Construction Materials',
                    'unit': 'each',
                    'unit_price': Decimal('100') * (i+1),
                    'cost_price': Decimal('60') * (i+1),
                    'reorder_level': 10,
                    'reorder_quantity': 50,
                }
            )
            products.append(product)
        
        for wh_id, warehouse in warehouses.items():
            for product in products:
                qty = 100 + (hash(f'{wh_id}-{product.id}') % 500)
                StockItem.objects.update_or_create(
                    product=product,
                    warehouse=warehouse,
                    defaults={
                        'quantity': qty,
                        'reserved_quantity': int(qty * 0.1),
                        'available_quantity': int(qty * 0.9),
                        'location': f'Aisle {(hash(product.id) % 10) + 1}',
                        'last_counted_at': timezone.now() - timedelta(days=7),
                    }
                )
            self.stdout.write(f'  Created stock items for warehouse {wh_id}')
        
        return products
