"""
Django management command to seed realistic mock data for ConstructOS.
This generates comprehensive test data for a construction management company.
"""

import uuid
import random
from datetime import datetime, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.hashers import make_password

from backend.apps.core.models import User, Event, AuditLog
from backend.apps.crm.models import (
    Account, Contact, Address, PipelineStage, Lead, Opportunity,
    Campaign, MailingList, Segment, Sla, Ticket, TicketComment, Client
)
from backend.apps.erp.models import (
    Warehouse, Product, StockItem, Invoice, InvoiceLineItem, Payment,
    GeneralLedgerEntry, Employee, PayrollRecord, LeaveRequest,
    SalesOrder, SalesOrderLineItem, PurchaseOrder, PurchaseOrderLineItem
)
from backend.apps.construction.models import (
    Project, Transaction, Equipment, SafetyInspection, Document
)


class Command(BaseCommand):
    help = 'Seed database with realistic construction company data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )

    def handle(self, *args, **options):
        self.stdout.write('Starting data seed...')
        
        if options['clear']:
            self.clear_data()
        
        with transaction.atomic():
            users = self.create_users()
            accounts = self.create_accounts(users)
            contacts = self.create_contacts(accounts, users)
            addresses = self.create_addresses(accounts, contacts)
            pipeline_stages = self.create_pipeline_stages()
            leads = self.create_leads(users)
            opportunities = self.create_opportunities(accounts, contacts, pipeline_stages, users)
            campaigns = self.create_campaigns(users)
            mailing_lists = self.create_mailing_lists()
            segments = self.create_segments()
            slas = self.create_slas()
            tickets = self.create_tickets(accounts, contacts, slas, users)
            
            warehouses = self.create_warehouses(users)
            products = self.create_products()
            stock_items = self.create_stock_items(products, warehouses)
            employees = self.create_employees(users)
            
            projects = self.create_projects(accounts, users)
            invoices = self.create_invoices(accounts, contacts, products)
            payments = self.create_payments(invoices, accounts)
            gl_entries = self.create_gl_entries(invoices, payments)
            
            sales_orders = self.create_sales_orders(accounts, contacts, opportunities, products, users)
            purchase_orders = self.create_purchase_orders(accounts, products, warehouses, users)
            
            transactions = self.create_transactions(projects)
            equipment = self.create_equipment(warehouses, employees)
            inspections = self.create_safety_inspections(projects)
            documents = self.create_documents(projects)
            
            payroll = self.create_payroll_records(employees)
            leave_requests = self.create_leave_requests(employees, users)
            
        self.stdout.write(self.style.SUCCESS('Successfully seeded all data!'))

    def clear_data(self):
        self.stdout.write('Clearing existing data...')
        models_to_clear = [
            Document, SafetyInspection, Transaction, Equipment, Project,
            PayrollRecord, LeaveRequest, PurchaseOrderLineItem, PurchaseOrder,
            SalesOrderLineItem, SalesOrder, GeneralLedgerEntry, Payment,
            InvoiceLineItem, Invoice, StockItem, Product, Warehouse, Employee,
            TicketComment, Ticket, Sla, Segment, MailingList, Campaign,
            Opportunity, Lead, PipelineStage, Client, Address, Contact, Account,
            AuditLog, Event, User
        ]
        for model in models_to_clear:
            model.objects.all().delete()
        self.stdout.write('Data cleared.')

    def create_users(self):
        self.stdout.write('Creating users...')
        users_data = [
            {'username': 'admin', 'email': 'admin@constructos.com', 'first_name': 'System', 'last_name': 'Administrator', 'role': 'admin', 'department': 'IT'},
            {'username': 'jmartinez', 'email': 'j.martinez@constructos.com', 'first_name': 'James', 'last_name': 'Martinez', 'role': 'executive', 'department': 'Executive'},
            {'username': 'schen', 'email': 's.chen@constructos.com', 'first_name': 'Sarah', 'last_name': 'Chen', 'role': 'project_manager', 'department': 'Operations'},
            {'username': 'mwilliams', 'email': 'm.williams@constructos.com', 'first_name': 'Michael', 'last_name': 'Williams', 'role': 'project_manager', 'department': 'Operations'},
            {'username': 'ejohnson', 'email': 'e.johnson@constructos.com', 'first_name': 'Emily', 'last_name': 'Johnson', 'role': 'finance', 'department': 'Finance'},
            {'username': 'dbrown', 'email': 'd.brown@constructos.com', 'first_name': 'David', 'last_name': 'Brown', 'role': 'warehouse', 'department': 'Logistics'},
            {'username': 'agarcia', 'email': 'a.garcia@constructos.com', 'first_name': 'Ana', 'last_name': 'Garcia', 'role': 'sales', 'department': 'Sales'},
            {'username': 'rthompson', 'email': 'r.thompson@constructos.com', 'first_name': 'Robert', 'last_name': 'Thompson', 'role': 'safety', 'department': 'Safety'},
        ]
        
        users = []
        for data in users_data:
            user = User.objects.create(
                id=str(uuid.uuid4()),
                password=make_password('password123'),
                **data
            )
            users.append(user)
        return users

    def create_accounts(self, users):
        self.stdout.write('Creating accounts...')
        accounts_data = [
            {'name': 'Meridian Development Group', 'legal_name': 'Meridian Development Group LLC', 'type': 'customer', 'industry': 'Real Estate Development', 'tier': 'Enterprise', 'annual_revenue': Decimal('85000000'), 'employee_count': 450, 'payment_terms': 'net_30', 'credit_limit': Decimal('500000'), 'account_number': 'ACC-001'},
            {'name': 'Pacific Coast Builders', 'legal_name': 'Pacific Coast Builders Inc.', 'type': 'customer', 'industry': 'General Contractor', 'tier': 'Enterprise', 'annual_revenue': Decimal('120000000'), 'employee_count': 800, 'payment_terms': 'net_45', 'credit_limit': Decimal('750000'), 'account_number': 'ACC-002'},
            {'name': 'Summit Construction Partners', 'legal_name': 'Summit Construction Partners LP', 'type': 'customer', 'industry': 'Commercial Construction', 'tier': 'Mid-Market', 'annual_revenue': Decimal('45000000'), 'employee_count': 280, 'payment_terms': 'net_30', 'credit_limit': Decimal('300000'), 'account_number': 'ACC-003'},
            {'name': 'Bay Area Steel Supply', 'legal_name': 'Bay Area Steel Supply Corp', 'type': 'vendor', 'industry': 'Steel Manufacturing', 'tier': 'Strategic', 'annual_revenue': Decimal('200000000'), 'employee_count': 1200, 'payment_terms': 'net_15', 'credit_limit': Decimal('1000000'), 'account_number': 'ACC-004'},
            {'name': 'Coastal Concrete Solutions', 'legal_name': 'Coastal Concrete Solutions Inc.', 'type': 'vendor', 'industry': 'Concrete Supply', 'tier': 'Preferred', 'annual_revenue': Decimal('35000000'), 'employee_count': 180, 'payment_terms': 'net_30', 'credit_limit': Decimal('250000'), 'account_number': 'ACC-005'},
            {'name': 'TechBuild Systems', 'legal_name': 'TechBuild Systems LLC', 'type': 'customer', 'industry': 'Technology', 'tier': 'Mid-Market', 'annual_revenue': Decimal('28000000'), 'employee_count': 150, 'payment_terms': 'net_30', 'credit_limit': Decimal('200000'), 'account_number': 'ACC-006'},
            {'name': 'Greenfield Municipal Authority', 'legal_name': 'City of Greenfield', 'type': 'customer', 'industry': 'Government', 'tier': 'Enterprise', 'annual_revenue': None, 'employee_count': 2500, 'payment_terms': 'net_60', 'credit_limit': Decimal('2000000'), 'account_number': 'ACC-007'},
            {'name': 'Westside Equipment Rentals', 'legal_name': 'Westside Equipment Rentals LLC', 'type': 'vendor', 'industry': 'Equipment Rental', 'tier': 'Standard', 'annual_revenue': Decimal('12000000'), 'employee_count': 45, 'payment_terms': 'net_15', 'credit_limit': Decimal('100000'), 'account_number': 'ACC-008'},
            {'name': 'Northern Electric Co.', 'legal_name': 'Northern Electric Company Inc.', 'type': 'vendor', 'industry': 'Electrical Supply', 'tier': 'Preferred', 'annual_revenue': Decimal('55000000'), 'employee_count': 320, 'payment_terms': 'net_30', 'credit_limit': Decimal('400000'), 'account_number': 'ACC-009'},
            {'name': 'Harbor View Properties', 'legal_name': 'Harbor View Properties LP', 'type': 'customer', 'industry': 'Property Management', 'tier': 'Mid-Market', 'annual_revenue': Decimal('18000000'), 'employee_count': 75, 'payment_terms': 'net_30', 'credit_limit': Decimal('150000'), 'account_number': 'ACC-010'},
            {'name': 'Mountain Ridge Developments', 'legal_name': 'Mountain Ridge Developments Inc.', 'type': 'prospect', 'industry': 'Residential Development', 'tier': 'Mid-Market', 'annual_revenue': Decimal('32000000'), 'employee_count': 120, 'payment_terms': 'net_30', 'credit_limit': Decimal('200000'), 'account_number': 'ACC-011'},
            {'name': 'Allied Plumbing Systems', 'legal_name': 'Allied Plumbing Systems Corp', 'type': 'vendor', 'industry': 'Plumbing Supply', 'tier': 'Standard', 'annual_revenue': Decimal('22000000'), 'employee_count': 95, 'payment_terms': 'net_30', 'credit_limit': Decimal('150000'), 'account_number': 'ACC-012'},
        ]
        
        accounts = []
        owner = random.choice(users)
        for data in accounts_data:
            account = Account.objects.create(
                id=str(uuid.uuid4()),
                website=f"https://www.{data['name'].lower().replace(' ', '')}.com",
                phone=f"+1 (555) {random.randint(100,999)}-{random.randint(1000,9999)}",
                email=f"info@{data['name'].lower().replace(' ', '')}.com",
                status='active',
                currency='USD',
                owner=random.choice(users),
                **data
            )
            accounts.append(account)
        
        accounts[2].parent_account = accounts[1]
        accounts[2].save()
        
        return accounts

    def create_contacts(self, accounts, users):
        self.stdout.write('Creating contacts...')
        first_names = ['John', 'Jennifer', 'Michael', 'Sarah', 'David', 'Lisa', 'Robert', 'Maria', 'William', 'Amanda', 'James', 'Patricia', 'Richard', 'Linda', 'Thomas', 'Barbara', 'Christopher', 'Elizabeth', 'Daniel', 'Susan', 'Matthew', 'Jessica', 'Anthony', 'Karen', 'Mark']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson', 'White', 'Harris']
        titles = ['CEO', 'CFO', 'COO', 'VP of Operations', 'Project Director', 'Procurement Manager', 'Construction Manager', 'Site Supervisor', 'Finance Director', 'Purchasing Agent', 'Contract Administrator', 'Safety Director', 'Quality Manager', 'Engineering Manager', 'Estimator']
        departments = ['Executive', 'Operations', 'Finance', 'Procurement', 'Engineering', 'Project Management', 'Safety', 'Quality Assurance', 'Administration']
        
        contacts = []
        for i, account in enumerate(accounts):
            num_contacts = random.randint(2, 4)
            for j in range(num_contacts):
                first = random.choice(first_names)
                last = random.choice(last_names)
                email_domain = account.name.lower().replace(' ', '') + '.com'
                contact = Contact.objects.create(
                    id=str(uuid.uuid4()),
                    first_name=first,
                    last_name=last,
                    email=f"{first.lower()}.{last.lower()}@{email_domain}",
                    phone=f"+1 (555) {random.randint(100,999)}-{random.randint(1000,9999)}",
                    mobile=f"+1 (555) {random.randint(100,999)}-{random.randint(1000,9999)}",
                    title=random.choice(titles),
                    department=random.choice(departments),
                    account=account,
                    is_primary=(j == 0),
                    preferred_communication=random.choice(['email', 'phone', 'email', 'email']),
                    status='active',
                    source=random.choice(['Website', 'Referral', 'Trade Show', 'LinkedIn', 'Cold Call']),
                    owner=random.choice(users),
                )
                contacts.append(contact)
        return contacts

    def create_addresses(self, accounts, contacts):
        self.stdout.write('Creating addresses...')
        cities_states = [
            ('San Francisco', 'CA', '94102'), ('Los Angeles', 'CA', '90001'), ('San Diego', 'CA', '92101'),
            ('Seattle', 'WA', '98101'), ('Portland', 'OR', '97201'), ('Denver', 'CO', '80202'),
            ('Phoenix', 'AZ', '85001'), ('Las Vegas', 'NV', '89101'), ('Austin', 'TX', '78701'),
            ('Houston', 'TX', '77001'), ('Dallas', 'TX', '75201'), ('Chicago', 'IL', '60601'),
        ]
        street_names = ['Main St', 'Oak Ave', 'Industrial Blvd', 'Commerce Dr', 'Technology Way', 'Enterprise Rd', 'Corporate Pkwy', 'Business Center Dr', 'Park Ave', 'Harbor Blvd']
        
        addresses = []
        for account in accounts:
            for addr_type in ['billing', 'shipping']:
                city, state, postal = random.choice(cities_states)
                address = Address.objects.create(
                    id=str(uuid.uuid4()),
                    street=f"{random.randint(100, 9999)} {random.choice(street_names)}",
                    street2=random.choice([None, 'Suite 100', 'Floor 5', 'Building A', None, None]),
                    city=city,
                    state=state,
                    postal_code=postal,
                    country='USA',
                    type=addr_type,
                    is_primary=True,
                    account=account,
                )
                addresses.append(address)
        return addresses

    def create_pipeline_stages(self):
        self.stdout.write('Creating pipeline stages...')
        stages_data = [
            {'name': 'Qualification', 'order': 1, 'probability': 10, 'color': '#6B7280'},
            {'name': 'Proposal Sent', 'order': 2, 'probability': 25, 'color': '#3B82F6'},
            {'name': 'Negotiation', 'order': 3, 'probability': 50, 'color': '#F59E0B'},
            {'name': 'Contract Review', 'order': 4, 'probability': 75, 'color': '#8B5CF6'},
            {'name': 'Closed Won', 'order': 5, 'probability': 100, 'color': '#10B981'},
            {'name': 'Closed Lost', 'order': 6, 'probability': 0, 'color': '#EF4444'},
        ]
        
        stages = []
        for data in stages_data:
            stage = PipelineStage.objects.create(id=str(uuid.uuid4()), **data)
            stages.append(stage)
        return stages

    def create_leads(self, users):
        self.stdout.write('Creating leads...')
        companies = ['Sunrise Properties', 'Metro Construction', 'Skyline Developers', 'Urban Build Co', 'Premier Contractors', 'Innovative Structures', 'Capital Building Group', 'Landmark Construction', 'Foundation First Inc', 'BuildRight Solutions', 'Elite Development Corp', 'Progressive Builders', 'NextGen Construction', 'Apex Building Systems', 'Cornerstone Projects', 'Alliance Contractors', 'Prime Development LLC', 'Structural Excellence']
        first_names = ['Alex', 'Jordan', 'Taylor', 'Morgan', 'Casey', 'Riley', 'Jamie', 'Cameron', 'Quinn', 'Avery', 'Blake', 'Drew', 'Parker', 'Skyler', 'Reese', 'Finley', 'Charlie', 'Hayden']
        last_names = ['Adams', 'Baker', 'Clark', 'Davis', 'Evans', 'Foster', 'Green', 'Hall', 'Irving', 'Jones', 'King', 'Lewis', 'Morris', 'Nelson', 'Owen', 'Price', 'Quinn', 'Reed']
        sources = ['Website Form', 'Trade Show', 'Referral', 'LinkedIn', 'Cold Outreach', 'Industry Event', 'Partner Referral', 'Google Ads']
        statuses = ['new', 'contacted', 'qualified', 'unqualified', 'converted']
        ratings = ['Hot', 'Warm', 'Cold']
        
        leads = []
        for i in range(18):
            first = random.choice(first_names)
            last = random.choice(last_names)
            company = random.choice(companies)
            lead = Lead.objects.create(
                id=str(uuid.uuid4()),
                first_name=first,
                last_name=last,
                email=f"{first.lower()}.{last.lower()}@{company.lower().replace(' ', '')}.com",
                phone=f"+1 (555) {random.randint(100,999)}-{random.randint(1000,9999)}",
                company=company,
                title=random.choice(['Owner', 'President', 'VP Operations', 'Director', 'Manager', 'Procurement Lead']),
                source=random.choice(sources),
                status=random.choice(statuses),
                rating=random.choice(ratings),
                estimated_value=Decimal(random.randint(50000, 5000000)),
                description=f"Interested in construction services for upcoming {random.choice(['commercial', 'residential', 'mixed-use', 'industrial'])} project.",
                owner=random.choice(users),
            )
            leads.append(lead)
        return leads

    def create_opportunities(self, accounts, contacts, stages, users):
        self.stdout.write('Creating opportunities...')
        project_types = ['Office Building Construction', 'Warehouse Development', 'Retail Center Build', 'Residential Complex', 'Hospital Renovation', 'School Construction', 'Mixed-Use Development', 'Industrial Facility', 'Hotel Construction', 'Data Center Build', 'Airport Terminal Expansion', 'Stadium Renovation']
        
        opportunities = []
        customer_accounts = [a for a in accounts if a.type == 'customer']
        
        for i in range(12):
            account = random.choice(customer_accounts)
            account_contacts = [c for c in contacts if c.account_id == account.id]
            contact = random.choice(account_contacts) if account_contacts else None
            stage = random.choice(stages[:5])
            close_date = timezone.now() + timedelta(days=random.randint(30, 180))
            
            opp = Opportunity.objects.create(
                id=str(uuid.uuid4()),
                name=f"{account.name} - {random.choice(project_types)}",
                account=account,
                contact=contact,
                stage=stage,
                amount=Decimal(random.randint(500000, 25000000)),
                probability=stage.probability,
                close_date=close_date,
                type=random.choice(['New Business', 'Expansion', 'Renovation']),
                source=random.choice(['Referral', 'Website', 'Trade Show', 'Existing Client']),
                description=f"Multi-phase construction project for {account.name}.",
                status='open' if stage.probability > 0 else 'closed',
                owner=random.choice(users),
            )
            opportunities.append(opp)
        return opportunities

    def create_campaigns(self, users):
        self.stdout.write('Creating campaigns...')
        campaigns_data = [
            {'name': 'Q1 Trade Show Series 2024', 'type': 'Trade Show', 'status': 'completed', 'budget': Decimal('75000'), 'actual_cost': Decimal('68500'), 'expected_revenue': Decimal('500000'), 'actual_revenue': Decimal('450000')},
            {'name': 'Commercial Construction Email Campaign', 'type': 'Email', 'status': 'active', 'budget': Decimal('15000'), 'actual_cost': Decimal('8500'), 'expected_revenue': Decimal('200000'), 'actual_revenue': Decimal('85000')},
            {'name': 'LinkedIn Sponsored Content - Q2', 'type': 'Social Media', 'status': 'active', 'budget': Decimal('25000'), 'actual_cost': Decimal('12000'), 'expected_revenue': Decimal('150000'), 'actual_revenue': Decimal('45000')},
            {'name': 'Industry Conference Sponsorship', 'type': 'Sponsorship', 'status': 'planned', 'budget': Decimal('100000'), 'actual_cost': Decimal('0'), 'expected_revenue': Decimal('750000'), 'actual_revenue': Decimal('0')},
        ]
        
        campaigns = []
        for data in campaigns_data:
            campaign = Campaign.objects.create(
                id=str(uuid.uuid4()),
                start_date=timezone.now() - timedelta(days=random.randint(30, 90)),
                end_date=timezone.now() + timedelta(days=random.randint(30, 90)),
                description=f"Marketing campaign targeting construction industry clients.",
                target_audience='General Contractors, Developers, Property Managers',
                owner=random.choice(users),
                **data
            )
            campaigns.append(campaign)
        return campaigns

    def create_slas(self):
        self.stdout.write('Creating SLAs...')
        slas_data = [
            {'name': 'Enterprise Priority', 'response_time_hours': 1, 'resolution_time_hours': 4, 'priority': 'critical'},
            {'name': 'Business Standard', 'response_time_hours': 4, 'resolution_time_hours': 24, 'priority': 'high'},
            {'name': 'General Support', 'response_time_hours': 8, 'resolution_time_hours': 48, 'priority': 'medium'},
        ]
        
        slas = []
        for data in slas_data:
            sla = Sla.objects.create(
                id=str(uuid.uuid4()),
                description=f"SLA for {data['priority']} priority tickets",
                **data
            )
            slas.append(sla)
        return slas

    def create_tickets(self, accounts, contacts, slas, users):
        self.stdout.write('Creating tickets...')
        subjects = [
            'Invoice discrepancy on project materials', 'Delivery delay for steel beams',
            'Quality issue with concrete batch #4521', 'Request for project timeline update',
            'Equipment maintenance scheduling', 'Safety certification renewal needed',
            'Change order approval required', 'Billing address update request',
            'Material substitution inquiry', 'Warranty claim for defective parts'
        ]
        
        tickets = []
        customer_accounts = [a for a in accounts if a.type == 'customer']
        
        for i in range(10):
            account = random.choice(customer_accounts)
            account_contacts = [c for c in contacts if c.account_id == account.id]
            contact = random.choice(account_contacts) if account_contacts else None
            
            ticket = Ticket.objects.create(
                id=str(uuid.uuid4()),
                ticket_number=f"TKT-{2024}{str(i+1).zfill(4)}",
                subject=random.choice(subjects),
                description=f"Customer reported issue requiring attention. Account: {account.name}",
                status=random.choice(['open', 'in_progress', 'pending', 'resolved', 'closed']),
                priority=random.choice(['low', 'medium', 'high', 'critical']),
                type=random.choice(['Support', 'Billing', 'Technical', 'General Inquiry']),
                source=random.choice(['Email', 'Phone', 'Portal', 'Chat']),
                account=account,
                contact=contact,
                assigned_to=random.choice(users),
                sla=random.choice(slas),
                due_date=timezone.now() + timedelta(hours=random.randint(4, 72)),
            )
            tickets.append(ticket)
            
            for j in range(random.randint(1, 4)):
                TicketComment.objects.create(
                    id=str(uuid.uuid4()),
                    ticket=ticket,
                    author=random.choice(users),
                    content=f"Update on ticket: {random.choice(['Investigating issue', 'Contacted customer', 'Awaiting response', 'Resolution in progress', 'Escalated to supervisor'])}",
                    is_internal=random.choice([True, False]),
                )
        
        return tickets

    def create_warehouses(self, users):
        self.stdout.write('Creating warehouses...')
        warehouses_data = [
            {'name': 'Main Distribution Center', 'code': 'WH-MAIN', 'address': '1500 Industrial Parkway', 'city': 'Oakland', 'country': 'USA', 'capacity': 50000},
            {'name': 'South Bay Storage Facility', 'code': 'WH-SBAY', 'address': '2800 Commerce Drive', 'city': 'San Jose', 'country': 'USA', 'capacity': 35000},
            {'name': 'North Region Depot', 'code': 'WH-NORTH', 'address': '890 Warehouse Road', 'city': 'Sacramento', 'country': 'USA', 'capacity': 25000},
        ]
        
        warehouses = []
        for data in warehouses_data:
            warehouse = Warehouse.objects.create(
                id=str(uuid.uuid4()),
                manager=random.choice(users),
                **data
            )
            warehouses.append(warehouse)
        return warehouses

    def create_products(self):
        self.stdout.write('Creating products...')
        products_data = [
            {'sku': 'STL-BEAM-W8X31', 'name': 'Steel Wide Flange Beam W8x31', 'category': 'Structural Steel', 'unit': 'linear_foot', 'unit_price': Decimal('45.00'), 'cost_price': Decimal('32.00'), 'reorder_level': 100, 'reorder_quantity': 500},
            {'sku': 'STL-BEAM-W12X40', 'name': 'Steel Wide Flange Beam W12x40', 'category': 'Structural Steel', 'unit': 'linear_foot', 'unit_price': Decimal('62.00'), 'cost_price': Decimal('44.00'), 'reorder_level': 75, 'reorder_quantity': 400},
            {'sku': 'CON-RMX-4000PSI', 'name': 'Ready-Mix Concrete 4000 PSI', 'category': 'Concrete', 'unit': 'cubic_yard', 'unit_price': Decimal('145.00'), 'cost_price': Decimal('98.00'), 'reorder_level': 50, 'reorder_quantity': 200},
            {'sku': 'CON-RMX-5000PSI', 'name': 'Ready-Mix Concrete 5000 PSI', 'category': 'Concrete', 'unit': 'cubic_yard', 'unit_price': Decimal('165.00'), 'cost_price': Decimal('112.00'), 'reorder_level': 40, 'reorder_quantity': 150},
            {'sku': 'RBR-GR60-4', 'name': 'Rebar Grade 60 #4', 'category': 'Reinforcement', 'unit': 'ton', 'unit_price': Decimal('1150.00'), 'cost_price': Decimal('820.00'), 'reorder_level': 20, 'reorder_quantity': 100},
            {'sku': 'RBR-GR60-6', 'name': 'Rebar Grade 60 #6', 'category': 'Reinforcement', 'unit': 'ton', 'unit_price': Decimal('1180.00'), 'cost_price': Decimal('845.00'), 'reorder_level': 20, 'reorder_quantity': 100},
            {'sku': 'LUM-2X4-SPF', 'name': 'Lumber 2x4 SPF Stud Grade', 'category': 'Lumber', 'unit': 'board_foot', 'unit_price': Decimal('4.50'), 'cost_price': Decimal('2.80'), 'reorder_level': 500, 'reorder_quantity': 2000},
            {'sku': 'LUM-PLY-3/4', 'name': 'Plywood 3/4" CDX Sheathing', 'category': 'Lumber', 'unit': 'sheet', 'unit_price': Decimal('52.00'), 'cost_price': Decimal('36.00'), 'reorder_level': 100, 'reorder_quantity': 500},
            {'sku': 'ELC-WIRE-12AWG', 'name': 'Electrical Wire 12 AWG THHN', 'category': 'Electrical', 'unit': 'foot', 'unit_price': Decimal('0.85'), 'cost_price': Decimal('0.55'), 'reorder_level': 2000, 'reorder_quantity': 10000},
            {'sku': 'ELC-PANEL-200A', 'name': 'Main Breaker Panel 200A', 'category': 'Electrical', 'unit': 'each', 'unit_price': Decimal('485.00'), 'cost_price': Decimal('325.00'), 'reorder_level': 10, 'reorder_quantity': 25},
            {'sku': 'PLB-PIPE-CU-1', 'name': 'Copper Pipe Type L 1"', 'category': 'Plumbing', 'unit': 'linear_foot', 'unit_price': Decimal('12.50'), 'cost_price': Decimal('8.20'), 'reorder_level': 200, 'reorder_quantity': 1000},
            {'sku': 'PLB-PIPE-PVC-4', 'name': 'PVC Drain Pipe Schedule 40 4"', 'category': 'Plumbing', 'unit': 'linear_foot', 'unit_price': Decimal('8.75'), 'cost_price': Decimal('5.40'), 'reorder_level': 300, 'reorder_quantity': 1500},
            {'sku': 'HVC-DUCT-24X12', 'name': 'HVAC Ductwork 24"x12"', 'category': 'HVAC', 'unit': 'linear_foot', 'unit_price': Decimal('28.00'), 'cost_price': Decimal('18.50'), 'reorder_level': 100, 'reorder_quantity': 400},
            {'sku': 'INS-BATT-R30', 'name': 'Fiberglass Insulation R-30', 'category': 'Insulation', 'unit': 'square_foot', 'unit_price': Decimal('1.85'), 'cost_price': Decimal('1.15'), 'reorder_level': 1000, 'reorder_quantity': 5000},
            {'sku': 'DRY-GYP-1/2', 'name': 'Drywall Gypsum Board 1/2"', 'category': 'Drywall', 'unit': 'sheet', 'unit_price': Decimal('14.50'), 'cost_price': Decimal('9.20'), 'reorder_level': 200, 'reorder_quantity': 1000},
            {'sku': 'HRD-BOLT-1/2X4', 'name': 'Hex Bolt Grade 5 1/2"x4"', 'category': 'Hardware', 'unit': 'box', 'unit_price': Decimal('45.00'), 'cost_price': Decimal('28.00'), 'reorder_level': 50, 'reorder_quantity': 200},
            {'sku': 'HRD-ANCHOR-3/4', 'name': 'Wedge Anchor 3/4"x6"', 'category': 'Hardware', 'unit': 'box', 'unit_price': Decimal('125.00'), 'cost_price': Decimal('82.00'), 'reorder_level': 30, 'reorder_quantity': 100},
            {'sku': 'SAF-HARNESS-FP', 'name': 'Fall Protection Harness', 'category': 'Safety Equipment', 'unit': 'each', 'unit_price': Decimal('185.00'), 'cost_price': Decimal('120.00'), 'reorder_level': 20, 'reorder_quantity': 50},
            {'sku': 'SAF-HELMET-CL2', 'name': 'Hard Hat Class E Type II', 'category': 'Safety Equipment', 'unit': 'each', 'unit_price': Decimal('28.00'), 'cost_price': Decimal('16.00'), 'reorder_level': 50, 'reorder_quantity': 150},
            {'sku': 'TOL-LASER-ROT', 'name': 'Rotary Laser Level Kit', 'category': 'Tools', 'unit': 'each', 'unit_price': Decimal('750.00'), 'cost_price': Decimal('485.00'), 'reorder_level': 5, 'reorder_quantity': 15},
            {'sku': 'FRM-PLYWOOD-FORM', 'name': 'Concrete Form Plywood HDO', 'category': 'Formwork', 'unit': 'sheet', 'unit_price': Decimal('85.00'), 'cost_price': Decimal('58.00'), 'reorder_level': 75, 'reorder_quantity': 300},
            {'sku': 'WTR-MEMBRANE-60', 'name': 'Waterproofing Membrane 60 mil', 'category': 'Waterproofing', 'unit': 'square_foot', 'unit_price': Decimal('3.25'), 'cost_price': Decimal('2.10'), 'reorder_level': 500, 'reorder_quantity': 2500},
            {'sku': 'RNT-CRANE-50T', 'name': 'Crane Rental 50 Ton (Daily)', 'category': 'Equipment Rental', 'unit': 'day', 'unit_price': Decimal('2500.00'), 'cost_price': Decimal('1800.00'), 'reorder_level': 0, 'reorder_quantity': 0},
            {'sku': 'RNT-EXCAV-CAT320', 'name': 'Excavator CAT 320 Rental (Daily)', 'category': 'Equipment Rental', 'unit': 'day', 'unit_price': Decimal('850.00'), 'cost_price': Decimal('600.00'), 'reorder_level': 0, 'reorder_quantity': 0},
            {'sku': 'SVC-ENGINEERING', 'name': 'Structural Engineering Services', 'category': 'Professional Services', 'unit': 'hour', 'unit_price': Decimal('175.00'), 'cost_price': Decimal('125.00'), 'reorder_level': 0, 'reorder_quantity': 0},
            {'sku': 'SVC-SURVEY', 'name': 'Land Survey Services', 'category': 'Professional Services', 'unit': 'hour', 'unit_price': Decimal('145.00'), 'cost_price': Decimal('95.00'), 'reorder_level': 0, 'reorder_quantity': 0},
            {'sku': 'CON-GROUT-NSG', 'name': 'Non-Shrink Grout 50lb', 'category': 'Concrete', 'unit': 'bag', 'unit_price': Decimal('32.00'), 'cost_price': Decimal('21.00'), 'reorder_level': 100, 'reorder_quantity': 400},
            {'sku': 'STL-DECK-3B20', 'name': 'Steel Deck 3" B Gauge 20', 'category': 'Structural Steel', 'unit': 'square_foot', 'unit_price': Decimal('4.80'), 'cost_price': Decimal('3.25'), 'reorder_level': 1000, 'reorder_quantity': 5000},
            {'sku': 'WIN-DBL-6X4', 'name': 'Double Pane Window 6\'x4\'', 'category': 'Windows & Doors', 'unit': 'each', 'unit_price': Decimal('425.00'), 'cost_price': Decimal('285.00'), 'reorder_level': 15, 'reorder_quantity': 50},
            {'sku': 'DOR-EXT-36', 'name': 'Exterior Steel Door 36"', 'category': 'Windows & Doors', 'unit': 'each', 'unit_price': Decimal('385.00'), 'cost_price': Decimal('255.00'), 'reorder_level': 10, 'reorder_quantity': 30},
        ]
        
        products = []
        for data in products_data:
            product = Product.objects.create(
                id=str(uuid.uuid4()),
                description=f"High quality {data['name']} for construction projects",
                **data
            )
            products.append(product)
        return products

    def create_stock_items(self, products, warehouses):
        self.stdout.write('Creating stock items...')
        stock_items = []
        
        for product in products:
            if product.reorder_level == 0:
                continue
            for warehouse in warehouses:
                qty = random.randint(int(product.reorder_level * 0.5), int(product.reorder_quantity * 1.2))
                reserved = random.randint(0, int(qty * 0.3))
                stock = StockItem.objects.create(
                    id=str(uuid.uuid4()),
                    product=product,
                    warehouse=warehouse,
                    quantity=qty,
                    reserved_quantity=reserved,
                    available_quantity=qty - reserved,
                    location=f"Aisle {random.randint(1,20)}-Rack {random.choice(['A','B','C','D'])}-{random.randint(1,50)}",
                    last_counted_at=timezone.now() - timedelta(days=random.randint(1, 30)),
                )
                stock_items.append(stock)
        return stock_items

    def create_employees(self, users):
        self.stdout.write('Creating employees...')
        employees_data = [
            {'first_name': 'Marcus', 'last_name': 'Rodriguez', 'department': 'Operations', 'position': 'Site Superintendent', 'salary': Decimal('95000')},
            {'first_name': 'Jennifer', 'last_name': 'Walsh', 'department': 'Finance', 'position': 'Controller', 'salary': Decimal('125000')},
            {'first_name': 'Kevin', 'last_name': 'O\'Brien', 'department': 'Operations', 'position': 'Project Engineer', 'salary': Decimal('78000')},
            {'first_name': 'Lisa', 'last_name': 'Nakamura', 'department': 'Safety', 'position': 'Safety Manager', 'salary': Decimal('85000')},
            {'first_name': 'Carlos', 'last_name': 'Mendez', 'department': 'Operations', 'position': 'Crane Operator', 'salary': Decimal('72000')},
            {'first_name': 'Amanda', 'last_name': 'Foster', 'department': 'HR', 'position': 'HR Manager', 'salary': Decimal('82000')},
            {'first_name': 'Derek', 'last_name': 'Thompson', 'department': 'Logistics', 'position': 'Warehouse Supervisor', 'salary': Decimal('65000')},
            {'first_name': 'Michelle', 'last_name': 'Kim', 'department': 'Engineering', 'position': 'Structural Engineer', 'salary': Decimal('98000')},
            {'first_name': 'Brandon', 'last_name': 'Lewis', 'department': 'Operations', 'position': 'Foreman', 'salary': Decimal('68000')},
            {'first_name': 'Nicole', 'last_name': 'Patel', 'department': 'Procurement', 'position': 'Purchasing Manager', 'salary': Decimal('75000')},
            {'first_name': 'Ryan', 'last_name': 'Sullivan', 'department': 'Operations', 'position': 'Equipment Operator', 'salary': Decimal('58000')},
            {'first_name': 'Stephanie', 'last_name': 'Chen', 'department': 'Quality', 'position': 'QA Inspector', 'salary': Decimal('62000')},
            {'first_name': 'Antonio', 'last_name': 'Vasquez', 'department': 'Operations', 'position': 'Carpenter Lead', 'salary': Decimal('64000')},
            {'first_name': 'Rachel', 'last_name': 'Morrison', 'department': 'Administration', 'position': 'Office Manager', 'salary': Decimal('55000')},
            {'first_name': 'Tyler', 'last_name': 'Jackson', 'department': 'Operations', 'position': 'Electrician', 'salary': Decimal('72000')},
        ]
        
        employees = []
        for i, data in enumerate(employees_data):
            last_name_clean = data['last_name'].lower().replace("'", "")
            emp = Employee.objects.create(
                id=str(uuid.uuid4()),
                employee_number=f"EMP-{str(1001 + i)}",
                user=users[i % len(users)] if i < len(users) else None,
                email=f"{data['first_name'].lower()}.{last_name_clean}@constructos.com",
                phone=f"+1 (555) {random.randint(100,999)}-{random.randint(1000,9999)}",
                hire_date=timezone.now() - timedelta(days=random.randint(180, 1800)),
                salary_frequency='biweekly',
                status='active',
                address=f"{random.randint(100, 9999)} {random.choice(['Oak St', 'Main Ave', 'Park Blvd', 'Cedar Ln'])}",
                city=random.choice(['Oakland', 'San Francisco', 'Berkeley', 'Alameda']),
                country='USA',
                emergency_contact=f"{random.choice(['Spouse', 'Parent', 'Sibling'])}",
                emergency_phone=f"+1 (555) {random.randint(100,999)}-{random.randint(1000,9999)}",
                **data
            )
            employees.append(emp)
        return employees

    def create_projects(self, accounts, users):
        self.stdout.write('Creating projects...')
        projects_data = [
            {'name': 'Downtown Office Tower Phase 1', 'location': '450 Market Street, San Francisco, CA', 'status': 'In Progress', 'progress': 65, 'budget': Decimal('45000000'), 'description': 'Class A office tower development with 32 floors of premium office space and ground-level retail.'},
            {'name': 'Harbor View Medical Center', 'location': '1200 Harbor Blvd, Oakland, CA', 'status': 'In Progress', 'progress': 42, 'budget': Decimal('78000000'), 'description': 'State-of-the-art medical facility with emergency department, surgical suites, and patient tower.'},
            {'name': 'Greenfield Community Center', 'location': '5500 Greenfield Rd, Greenfield, CA', 'status': 'Planning', 'progress': 15, 'budget': Decimal('12000000'), 'description': 'Public community center with gymnasium, meeting rooms, and outdoor recreational facilities.'},
            {'name': 'Tech Campus Building B', 'location': '2000 Innovation Way, San Jose, CA', 'status': 'In Progress', 'progress': 78, 'budget': Decimal('32000000'), 'description': 'Second phase of technology campus expansion with open floor plan and collaboration spaces.'},
            {'name': 'Luxury Residential Complex', 'location': '800 Pacific Heights, San Francisco, CA', 'status': 'Completed', 'progress': 100, 'budget': Decimal('28000000'), 'description': 'High-end residential development with 45 luxury condominium units and premium amenities.'},
            {'name': 'Industrial Distribution Center', 'location': '15000 Industrial Pkwy, Fremont, CA', 'status': 'In Progress', 'progress': 55, 'budget': Decimal('18000000'), 'description': 'Modern logistics facility with automated storage systems and loading dock infrastructure.'},
            {'name': 'Airport Terminal Renovation', 'location': 'Oakland International Airport, Oakland, CA', 'status': 'On Hold', 'progress': 25, 'budget': Decimal('95000000'), 'description': 'Comprehensive terminal modernization including expanded gates and enhanced passenger experience.'},
            {'name': 'Waterfront Hotel Development', 'location': '100 Embarcadero, San Francisco, CA', 'status': 'Planning', 'progress': 8, 'budget': Decimal('65000000'), 'description': 'Boutique hotel with 250 rooms, rooftop restaurant, and conference facilities.'},
        ]
        
        projects = []
        customer_accounts = [a for a in accounts if a.type == 'customer']
        
        for i, data in enumerate(projects_data):
            start_date = timezone.now() - timedelta(days=random.randint(90, 365))
            due_date = start_date + timedelta(days=random.randint(365, 730))
            
            project = Project.objects.create(
                id=f"PRJ-{str(2024)}{str(i+1).zfill(3)}",
                due_date=due_date.strftime('%Y-%m-%d'),
                account=customer_accounts[i % len(customer_accounts)],
                manager=random.choice(users),
                start_date=start_date,
                **data
            )
            projects.append(project)
        return projects

    def create_invoices(self, accounts, contacts, products):
        self.stdout.write('Creating invoices...')
        invoices = []
        customer_accounts = [a for a in accounts if a.type == 'customer']
        
        for i in range(15):
            account = random.choice(customer_accounts)
            account_contacts = [c for c in contacts if c.account_id == account.id]
            contact = random.choice(account_contacts) if account_contacts else None
            
            issue_date = timezone.now() - timedelta(days=random.randint(1, 90))
            due_days = {'net_15': 15, 'net_30': 30, 'net_45': 45, 'net_60': 60, 'due_on_receipt': 0}.get(account.payment_terms, 30)
            due_date = issue_date + timedelta(days=due_days)
            
            subtotal = Decimal(random.randint(10000, 500000))
            tax_rate = Decimal('0.0875')
            tax_amount = subtotal * tax_rate
            total = subtotal + tax_amount
            
            status = random.choice(['draft', 'sent', 'paid', 'partial', 'overdue'])
            paid_amount = total if status == 'paid' else (total * Decimal(random.uniform(0.2, 0.8)) if status == 'partial' else Decimal('0'))
            
            invoice = Invoice.objects.create(
                id=str(uuid.uuid4()),
                invoice_number=f"INV-{2024}{str(i+1).zfill(4)}",
                account=account,
                contact=contact,
                status=status,
                due_date=due_date,
                subtotal=subtotal,
                tax_amount=tax_amount,
                total_amount=total,
                paid_amount=paid_amount.quantize(Decimal('0.01')),
                notes=f"Invoice for construction materials and services - {account.name}",
                terms=f"Payment due within {due_days} days of invoice date.",
            )
            invoices.append(invoice)
            
            num_items = random.randint(2, 6)
            selected_products = random.sample(products, min(num_items, len(products)))
            
            for product in selected_products:
                qty = Decimal(random.randint(1, 100))
                line_total = qty * product.unit_price
                InvoiceLineItem.objects.create(
                    id=str(uuid.uuid4()),
                    invoice=invoice,
                    product=product,
                    description=product.name,
                    quantity=qty,
                    unit_price=product.unit_price,
                    discount=Decimal('0'),
                    tax_rate=Decimal('8.75'),
                    total_amount=line_total,
                )
        
        return invoices

    def create_payments(self, invoices, accounts):
        self.stdout.write('Creating payments...')
        payments = []
        
        paid_invoices = [inv for inv in invoices if inv.status in ['paid', 'partial']]
        
        for i, invoice in enumerate(paid_invoices):
            payment = Payment.objects.create(
                id=str(uuid.uuid4()),
                payment_number=f"PAY-{2024}{str(i+1).zfill(4)}",
                invoice=invoice,
                account=invoice.account,
                amount=invoice.paid_amount,
                method=random.choice(['ACH', 'Wire Transfer', 'Check', 'Credit Card']),
                status='completed',
                reference=f"REF-{random.randint(100000, 999999)}",
                notes=f"Payment for Invoice {invoice.invoice_number}",
            )
            payments.append(payment)
        
        return payments

    def create_transactions(self, projects):
        self.stdout.write('Creating transactions...')
        transactions = []
        
        expense_categories = ['Materials', 'Labor', 'Equipment Rental', 'Subcontractor', 'Permits', 'Insurance', 'Utilities', 'Professional Services']
        revenue_categories = ['Progress Payment', 'Milestone Payment', 'Change Order', 'Final Payment']
        
        for project in projects:
            num_transactions = random.randint(8, 15)
            
            for i in range(num_transactions):
                is_expense = random.random() < 0.7
                
                trans = Transaction.objects.create(
                    id=str(uuid.uuid4()),
                    project=project,
                    description=f"{'Expense' if is_expense else 'Revenue'}: {random.choice(expense_categories if is_expense else revenue_categories)} for {project.name}",
                    amount=Decimal(random.randint(5000, 500000)),
                    status=random.choice(['pending', 'approved', 'completed']),
                    category=random.choice(expense_categories if is_expense else revenue_categories),
                    type='expense' if is_expense else 'revenue',
                )
                transactions.append(trans)
        
        return transactions

    def create_equipment(self, warehouses, employees):
        self.stdout.write('Creating equipment...')
        equipment_data = [
            {'name': 'Tower Crane TC-500', 'status': 'Active', 'serial_number': 'TC-2021-00145', 'purchase_price': Decimal('450000')},
            {'name': 'Excavator CAT 320GC', 'status': 'Active', 'serial_number': 'CAT-320-87456', 'purchase_price': Decimal('285000')},
            {'name': 'Concrete Pump Truck', 'status': 'Active', 'serial_number': 'CPT-2022-00089', 'purchase_price': Decimal('320000')},
            {'name': 'Boom Lift JLG 800AJ', 'status': 'Maintenance', 'serial_number': 'JLG-800-34521', 'purchase_price': Decimal('145000')},
            {'name': 'Backhoe Loader John Deere 310L', 'status': 'Active', 'serial_number': 'JD-310L-67890', 'purchase_price': Decimal('125000')},
            {'name': 'Scissor Lift Skyjack SJ6826', 'status': 'Active', 'serial_number': 'SJ-6826-45678', 'purchase_price': Decimal('42000')},
            {'name': 'Forklift Toyota 8FGU25', 'status': 'Active', 'serial_number': 'TYT-8FGU-12345', 'purchase_price': Decimal('35000')},
            {'name': 'Compactor Bomag BW120AD', 'status': 'Maintenance', 'serial_number': 'BOM-120AD-78901', 'purchase_price': Decimal('48000')},
            {'name': 'Bulldozer CAT D6', 'status': 'Active', 'serial_number': 'CAT-D6-23456', 'purchase_price': Decimal('380000')},
            {'name': 'Telehandler JCB 540-170', 'status': 'Active', 'serial_number': 'JCB-540-89012', 'purchase_price': Decimal('165000')},
            {'name': 'Wheel Loader Volvo L90H', 'status': 'Inactive', 'serial_number': 'VOL-L90H-34567', 'purchase_price': Decimal('295000')},
            {'name': 'Dump Truck Kenworth T880', 'status': 'Active', 'serial_number': 'KW-T880-56789', 'purchase_price': Decimal('175000')},
            {'name': 'Generator CAT XQ500', 'status': 'Active', 'serial_number': 'CAT-XQ500-01234', 'purchase_price': Decimal('85000')},
            {'name': 'Welding Machine Lincoln SA-200', 'status': 'Active', 'serial_number': 'LNC-SA200-67890', 'purchase_price': Decimal('12000')},
            {'name': 'Concrete Mixer Truck', 'status': 'Active', 'serial_number': 'CMT-2023-00156', 'purchase_price': Decimal('195000')},
            {'name': 'Mobile Crane Grove GMK5150L', 'status': 'Active', 'serial_number': 'GRV-GMK5-45678', 'purchase_price': Decimal('850000')},
            {'name': 'Asphalt Paver Volvo ABG7820', 'status': 'Maintenance', 'serial_number': 'VOL-ABG-90123', 'purchase_price': Decimal('425000')},
            {'name': 'Pile Driver Junttan PM25', 'status': 'Inactive', 'serial_number': 'JUN-PM25-12345', 'purchase_price': Decimal('580000')},
            {'name': 'Skid Steer Bobcat S650', 'status': 'Active', 'serial_number': 'BOB-S650-78901', 'purchase_price': Decimal('52000')},
            {'name': 'Trencher Ditch Witch RT80', 'status': 'Active', 'serial_number': 'DW-RT80-23456', 'purchase_price': Decimal('78000')},
        ]
        
        locations = ['Downtown SF Site', 'Oakland Medical Center', 'San Jose Tech Campus', 'Main Warehouse', 'South Bay Yard', 'North Region Depot']
        
        equipment = []
        for i, data in enumerate(equipment_data):
            next_service = timezone.now() + timedelta(days=random.randint(7, 90))
            
            equip = Equipment.objects.create(
                id=f"EQ-{str(2024)}{str(i+1).zfill(3)}",
                location=random.choice(locations),
                next_service=next_service.strftime('%Y-%m-%d'),
                purchase_date=timezone.now() - timedelta(days=random.randint(180, 1800)),
                warehouse=random.choice(warehouses),
                assigned_to=random.choice(employees) if random.random() > 0.3 else None,
                **data
            )
            equipment.append(equip)
        return equipment

    def create_safety_inspections(self, projects):
        self.stdout.write('Creating safety inspections...')
        inspection_types = ['Daily Walkthrough', 'Weekly Safety Audit', 'Monthly Compliance Review', 'OSHA Inspection', 'Equipment Safety Check', 'Fire Safety Inspection', 'Fall Protection Audit']
        inspectors = ['Lisa Nakamura', 'Robert Thompson', 'Maria Santos', 'Kevin Walsh', 'Diana Patel']
        
        findings_examples = [
            'All safety equipment in compliance',
            'Minor housekeeping issues noted - debris in walkway',
            'Fire extinguisher inspection tags current',
            'Fall protection equipment needs replacement',
            'First aid kit needs restocking',
            'Emergency exit signage adequate',
            'PPE compliance at 98%',
            'Scaffolding inspection tags verified',
        ]
        
        corrective_actions = [
            'No action required',
            'Immediate cleanup completed',
            'Equipment ordered for replacement',
            'Training session scheduled for next week',
            'Supplies ordered and expected delivery in 2 days',
            'Signage replacement in progress',
            'Individual counseling completed',
            'Third-party inspection scheduled',
        ]
        
        inspections = []
        for project in projects:
            num_inspections = random.randint(2, 5)
            
            for i in range(num_inspections):
                inspection = SafetyInspection.objects.create(
                    id=str(uuid.uuid4()),
                    site=project.location,
                    type=random.choice(inspection_types),
                    status=random.choice(['Completed', 'Pending Review', 'In Progress', 'Scheduled']),
                    inspector=random.choice(inspectors),
                    project=project,
                    notes=f"Regular safety inspection for {project.name}",
                    findings=random.choice(findings_examples),
                    corrective_actions=random.choice(corrective_actions),
                )
                inspections.append(inspection)
        
        return inspections

    def create_documents(self, projects):
        self.stdout.write('Creating documents...')
        doc_types = ['Contract', 'Drawing', 'Specification', 'RFI', 'Submittal', 'Change Order', 'Meeting Minutes', 'Permit', 'Insurance Certificate', 'Inspection Report']
        categories = ['Legal', 'Engineering', 'Architecture', 'Permits & Approvals', 'Submittals', 'Correspondence', 'Financial', 'Safety']
        authors = ['James Martinez', 'Sarah Chen', 'Michael Williams', 'Emily Johnson', 'David Brown']
        
        documents = []
        for project in projects:
            num_docs = random.randint(4, 8)
            
            for i in range(num_docs):
                doc_type = random.choice(doc_types)
                doc = Document.objects.create(
                    id=str(uuid.uuid4()),
                    name=f"{doc_type} - {project.name} - Rev {random.randint(1,5)}",
                    type=doc_type,
                    size=f"{random.randint(100, 15000)} KB",
                    author=random.choice(authors),
                    project=project,
                    category=random.choice(categories),
                    url=f"/documents/{project.id}/{doc_type.lower().replace(' ', '_')}_{random.randint(1000,9999)}.pdf",
                    version=random.randint(1, 5),
                )
                documents.append(doc)
        
        return documents

    def create_payroll_records(self, employees):
        self.stdout.write('Creating payroll records...')
        payroll_records = []
        
        for employee in employees:
            if not employee.salary:
                continue
                
            base_biweekly = employee.salary / Decimal('26')
            
            for period in range(6):
                period_end = timezone.now() - timedelta(days=period * 14)
                period_start = period_end - timedelta(days=14)
                
                overtime = Decimal(random.randint(0, 2000)) if random.random() > 0.6 else Decimal('0')
                bonus = Decimal(random.randint(500, 5000)) if random.random() > 0.9 else Decimal('0')
                
                gross = base_biweekly + overtime + bonus
                deductions = gross * Decimal('0.08')
                tax = gross * Decimal('0.25')
                net = gross - deductions - tax
                
                record = PayrollRecord.objects.create(
                    id=str(uuid.uuid4()),
                    employee=employee,
                    period_start=period_start,
                    period_end=period_end,
                    base_salary=base_biweekly,
                    overtime=overtime,
                    bonus=bonus,
                    deductions=deductions,
                    tax_amount=tax,
                    net_pay=net,
                    status='paid' if period > 0 else random.choice(['pending', 'paid']),
                    paid_date=period_end + timedelta(days=3) if period > 0 else None,
                )
                payroll_records.append(record)
        
        return payroll_records

    def create_leave_requests(self, employees, users):
        self.stdout.write('Creating leave requests...')
        leave_types = ['Vacation', 'Sick Leave', 'Personal Day', 'Family Leave', 'Bereavement', 'Jury Duty']
        
        leave_requests = []
        for _ in range(10):
            employee = random.choice(employees)
            start = timezone.now() + timedelta(days=random.randint(-30, 60))
            days = random.randint(1, 10)
            end = start + timedelta(days=days)
            
            status = random.choice(['pending', 'approved', 'denied', 'approved'])
            
            leave = LeaveRequest.objects.create(
                id=str(uuid.uuid4()),
                employee=employee,
                type=random.choice(leave_types),
                start_date=start,
                end_date=end,
                total_days=Decimal(days),
                reason=f"Request for {random.choice(['planned', 'urgent', 'scheduled'])} time off",
                status=status,
                approved_by=random.choice(users) if status == 'approved' else None,
                approved_at=timezone.now() if status == 'approved' else None,
            )
            leave_requests.append(leave)
        
        return leave_requests

    def create_mailing_lists(self):
        self.stdout.write('Creating mailing lists...')
        lists_data = [
            {'name': 'Construction Industry Newsletter', 'description': 'Monthly newsletter for construction industry updates and insights', 'member_count': 2450},
            {'name': 'Product Announcements', 'description': 'Updates on new products and services', 'member_count': 1830},
            {'name': 'Safety Alerts', 'description': 'Critical safety notifications and compliance updates', 'member_count': 3200},
            {'name': 'Trade Show Attendees 2024', 'description': 'Contacts from trade shows and industry events', 'member_count': 890},
            {'name': 'Preferred Vendor Partners', 'description': 'Key vendor contacts for procurement', 'member_count': 156},
        ]
        
        mailing_lists = []
        for data in lists_data:
            ml = MailingList.objects.create(
                id=str(uuid.uuid4()),
                is_active=True,
                **data
            )
            mailing_lists.append(ml)
        return mailing_lists

    def create_segments(self):
        self.stdout.write('Creating segments...')
        segments_data = [
            {'name': 'Enterprise Customers', 'description': 'Accounts with annual revenue > $50M', 'criteria': 'annual_revenue > 50000000 AND type = customer', 'member_count': 4},
            {'name': 'Active Project Leads', 'description': 'Leads with estimated value > $500K', 'criteria': 'status = active AND estimated_value > 500000', 'member_count': 8},
            {'name': 'Bay Area Contacts', 'description': 'Contacts located in SF Bay Area', 'criteria': 'city IN (San Francisco, Oakland, San Jose)', 'member_count': 45},
            {'name': 'High Priority Tickets', 'description': 'Open tickets with critical or high priority', 'criteria': 'status = open AND priority IN (critical, high)', 'member_count': 3},
        ]
        
        segments = []
        for data in segments_data:
            seg = Segment.objects.create(
                id=str(uuid.uuid4()),
                is_active=True,
                **data
            )
            segments.append(seg)
        return segments

    def create_gl_entries(self, invoices, payments):
        self.stdout.write('Creating general ledger entries...')
        gl_entries = []
        entry_num = 1
        
        for invoice in invoices:
            gl = GeneralLedgerEntry.objects.create(
                id=str(uuid.uuid4()),
                entry_number=f"GL-{2024}{str(entry_num).zfill(5)}",
                account_code='1200',
                account_name='Accounts Receivable',
                description=f"Invoice {invoice.invoice_number} - {invoice.account.name if invoice.account else 'Unknown'}",
                debit=invoice.total_amount,
                credit=Decimal('0'),
                balance=invoice.total_amount,
                reference=invoice.invoice_number,
                invoice=invoice,
            )
            gl_entries.append(gl)
            entry_num += 1
            
            gl_rev = GeneralLedgerEntry.objects.create(
                id=str(uuid.uuid4()),
                entry_number=f"GL-{2024}{str(entry_num).zfill(5)}",
                account_code='4000',
                account_name='Revenue - Construction Services',
                description=f"Revenue recognition - {invoice.invoice_number}",
                debit=Decimal('0'),
                credit=invoice.subtotal,
                balance=invoice.subtotal,
                reference=invoice.invoice_number,
                invoice=invoice,
            )
            gl_entries.append(gl_rev)
            entry_num += 1
        
        for payment in payments:
            gl_cash = GeneralLedgerEntry.objects.create(
                id=str(uuid.uuid4()),
                entry_number=f"GL-{2024}{str(entry_num).zfill(5)}",
                account_code='1000',
                account_name='Cash',
                description=f"Payment received - {payment.payment_number}",
                debit=payment.amount,
                credit=Decimal('0'),
                balance=payment.amount,
                reference=payment.payment_number,
                payment=payment,
            )
            gl_entries.append(gl_cash)
            entry_num += 1
            
            gl_ar = GeneralLedgerEntry.objects.create(
                id=str(uuid.uuid4()),
                entry_number=f"GL-{2024}{str(entry_num).zfill(5)}",
                account_code='1200',
                account_name='Accounts Receivable',
                description=f"AR reduction - {payment.payment_number}",
                debit=Decimal('0'),
                credit=payment.amount,
                balance=payment.amount,
                reference=payment.payment_number,
                payment=payment,
            )
            gl_entries.append(gl_ar)
            entry_num += 1
        
        return gl_entries

    def create_sales_orders(self, accounts, contacts, opportunities, products, users):
        self.stdout.write('Creating sales orders...')
        sales_orders = []
        customer_accounts = [a for a in accounts if a.type == 'customer']
        
        for i in range(10):
            account = random.choice(customer_accounts)
            account_contacts = [c for c in contacts if c.account_id == account.id]
            contact = random.choice(account_contacts) if account_contacts else None
            opportunity = random.choice(opportunities) if random.random() > 0.3 else None
            
            subtotal = Decimal(random.randint(25000, 250000))
            tax_rate = Decimal('0.0875')
            tax_amount = subtotal * tax_rate
            shipping = Decimal(random.randint(500, 5000))
            discount = subtotal * Decimal('0.05') if random.random() > 0.5 else Decimal('0')
            total = subtotal + tax_amount + shipping - discount
            
            order = SalesOrder.objects.create(
                id=str(uuid.uuid4()),
                order_number=f"SO-{2024}{str(i+1).zfill(4)}",
                account=account,
                contact=contact,
                opportunity=opportunity,
                status=random.choice(['draft', 'confirmed', 'in_progress', 'shipped', 'delivered']),
                delivery_date=timezone.now() + timedelta(days=random.randint(7, 45)),
                shipping_address=f"{random.randint(100, 9999)} Industrial Blvd, {random.choice(['Oakland', 'San Francisco', 'San Jose'])}, CA",
                billing_address=f"{random.randint(100, 9999)} Commerce Dr, {random.choice(['Oakland', 'San Francisco', 'San Jose'])}, CA",
                subtotal=subtotal,
                tax_amount=tax_amount,
                shipping_cost=shipping,
                discount=discount,
                total_amount=total,
                notes=f"Sales order for {account.name}",
                owner=random.choice(users),
            )
            sales_orders.append(order)
            
            num_items = random.randint(2, 5)
            selected_products = random.sample(products, min(num_items, len(products)))
            for product in selected_products:
                qty = Decimal(random.randint(1, 50))
                line_total = qty * product.unit_price
                SalesOrderLineItem.objects.create(
                    id=str(uuid.uuid4()),
                    sales_order=order,
                    product=product,
                    description=product.name,
                    quantity=qty,
                    unit_price=product.unit_price,
                    discount=Decimal('0'),
                    tax_rate=Decimal('8.75'),
                    total_amount=line_total,
                )
        
        return sales_orders

    def create_purchase_orders(self, accounts, products, warehouses, users):
        self.stdout.write('Creating purchase orders...')
        purchase_orders = []
        vendor_accounts = [a for a in accounts if a.type == 'vendor']
        
        for i in range(8):
            supplier = random.choice(vendor_accounts)
            warehouse = random.choice(warehouses)
            
            subtotal = Decimal(random.randint(15000, 150000))
            tax_rate = Decimal('0.0875')
            tax_amount = subtotal * tax_rate
            shipping = Decimal(random.randint(200, 2000))
            total = subtotal + tax_amount + shipping
            
            status = random.choice(['draft', 'approved', 'ordered', 'received', 'partial'])
            
            po = PurchaseOrder.objects.create(
                id=str(uuid.uuid4()),
                order_number=f"PO-{2024}{str(i+1).zfill(4)}",
                supplier=supplier,
                status=status,
                expected_delivery_date=timezone.now() + timedelta(days=random.randint(5, 30)),
                received_date=timezone.now() - timedelta(days=random.randint(1, 10)) if status == 'received' else None,
                warehouse=warehouse,
                subtotal=subtotal,
                tax_amount=tax_amount,
                shipping_cost=shipping,
                total_amount=total,
                notes=f"Purchase order from {supplier.name}",
                approved_by=random.choice(users) if status != 'draft' else None,
                approved_at=timezone.now() - timedelta(days=random.randint(1, 30)) if status != 'draft' else None,
            )
            purchase_orders.append(po)
            
            num_items = random.randint(2, 6)
            selected_products = random.sample(products, min(num_items, len(products)))
            for product in selected_products:
                qty = Decimal(random.randint(10, 200))
                line_total = qty * (product.cost_price or product.unit_price * Decimal('0.7'))
                received = qty if status == 'received' else (qty * Decimal('0.5') if status == 'partial' else Decimal('0'))
                PurchaseOrderLineItem.objects.create(
                    id=str(uuid.uuid4()),
                    purchase_order=po,
                    product=product,
                    description=product.name,
                    quantity=qty,
                    unit_price=product.cost_price or product.unit_price * Decimal('0.7'),
                    tax_rate=Decimal('8.75'),
                    total_amount=line_total,
                    received_quantity=received,
                )
        
        return purchase_orders
