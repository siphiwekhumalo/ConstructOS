"""
Django management command to seed realistic mock data for ConstructOS.
This generates comprehensive test data for a construction management company.

Uses Faker with seeding for consistent, reproducible data generation.
UUID maps are pre-generated to ensure referential integrity across services.
"""

import uuid
import random
from datetime import datetime, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.hashers import make_password
from faker import Faker

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

SEED = 42
fake = Faker('en_GB')  # English locale (SA data is manually configured)
Faker.seed(SEED)
random.seed(SEED)

SA_FIRST_NAMES = ['Thabo', 'Sipho', 'Nomvula', 'Lindiwe', 'Pieter', 'Johan', 'Andile', 'Kagiso', 'Mpho', 'Lerato', 
                  'Willem', 'Francois', 'Thandiwe', 'Bongani', 'Zanele', 'Mandla', 'Precious', 'Themba', 'Sibongile',
                  'Annemarie', 'Priya', 'Kobus', 'Hennie', 'Ntombi', 'Busisiwe', 'Dumi', 'Ayanda', 'Lebo', 'Neo', 'Tumi']
SA_LAST_NAMES = ['Molefe', 'Naidoo', 'Van der Merwe', 'Botha', 'Pretorius', 'Dlamini', 'Mthembu', 'Khumalo', 'Ndlovu', 
                 'Zulu', 'Swanepoel', 'Coetzee', 'Mokoena', 'Mahlangu', 'Sithole', 'Mabaso', 'Pillay', 'Govender',
                 'Van Wyk', 'Jansen', 'Kruger', 'Steyn', 'Du Plessis', 'Venter', 'Mkhize', 'Radebe', 'Mbeki', 'Tshabalala']

ACCOUNT_UUIDS = [str(uuid.UUID(int=random.getrandbits(128))) for _ in range(500)]
CONTACT_UUIDS = [str(uuid.UUID(int=random.getrandbits(128))) for _ in range(2000)]
PRODUCT_UUIDS = [str(uuid.UUID(int=random.getrandbits(128))) for _ in range(1000)]
PROJECT_UUIDS = [str(uuid.UUID(int=random.getrandbits(128))) for _ in range(200)]
EMPLOYEE_UUIDS = [str(uuid.UUID(int=random.getrandbits(128))) for _ in range(500)]
USER_UUIDS = [str(uuid.UUID(int=random.getrandbits(128))) for _ in range(50)]
INVOICE_UUIDS = [str(uuid.UUID(int=random.getrandbits(128))) for _ in range(1000)]
EQUIPMENT_UUIDS = [str(uuid.UUID(int=random.getrandbits(128))) for _ in range(500)]


class Command(BaseCommand):
    help = 'Seed database with realistic construction company data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )
        parser.add_argument(
            '--volume',
            type=str,
            default='medium',
            choices=['small', 'medium', 'large'],
            help='Data volume: small (current), medium (5x), large (10x)',
        )

    def handle(self, *args, **options):
        self.stdout.write('Starting data seed...')
        
        volume = options.get('volume', 'medium')
        self.volume_multiplier = {'small': 1, 'medium': 5, 'large': 10}.get(volume, 1)
        self.stdout.write(f'Volume: {volume} (multiplier: {self.volume_multiplier}x)')
        
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
        
        self.print_summary()
        self.stdout.write(self.style.SUCCESS('Successfully seeded all data!'))
    
    def print_summary(self):
        self.stdout.write('\n=== DATA SUMMARY ===')
        self.stdout.write(f'Users: {User.objects.count()}')
        self.stdout.write(f'Accounts: {Account.objects.count()}')
        self.stdout.write(f'Contacts: {Contact.objects.count()}')
        self.stdout.write(f'Products: {Product.objects.count()}')
        self.stdout.write(f'Projects: {Project.objects.count()}')
        self.stdout.write(f'Invoices: {Invoice.objects.count()}')
        self.stdout.write(f'Employees: {Employee.objects.count()}')
        self.stdout.write(f'Equipment: {Equipment.objects.count()}')
        self.stdout.write('====================')

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
        base_users = [
            {'username': 'admin', 'email': 'admin@constructos.co.za', 'first_name': 'System', 'last_name': 'Administrator', 'role': 'admin', 'department': 'IT'},
            {'username': 'tbotha', 'email': 't.botha@constructos.co.za', 'first_name': 'Thabo', 'last_name': 'Botha', 'role': 'executive', 'department': 'Executive'},
            {'username': 'snaidoo', 'email': 's.naidoo@constructos.co.za', 'first_name': 'Sibongile', 'last_name': 'Naidoo', 'role': 'project_manager', 'department': 'Operations'},
            {'username': 'jvandermerwe', 'email': 'j.vandermerwe@constructos.co.za', 'first_name': 'Johan', 'last_name': 'Van der Merwe', 'role': 'project_manager', 'department': 'Operations'},
            {'username': 'lpretorius', 'email': 'l.pretorius@constructos.co.za', 'first_name': 'Lindiwe', 'last_name': 'Pretorius', 'role': 'finance', 'department': 'Finance'},
            {'username': 'dswanepoel', 'email': 'd.swanepoel@constructos.co.za', 'first_name': 'David', 'last_name': 'Swanepoel', 'role': 'warehouse', 'department': 'Logistics'},
            {'username': 'nmolefe', 'email': 'n.molefe@constructos.co.za', 'first_name': 'Nomvula', 'last_name': 'Molefe', 'role': 'sales', 'department': 'Sales'},
            {'username': 'pjansen', 'email': 'p.jansen@constructos.co.za', 'first_name': 'Pieter', 'last_name': 'Jansen', 'role': 'safety', 'department': 'Safety'},
        ]
        
        users = []
        roles = ['admin', 'executive', 'project_manager', 'finance', 'warehouse', 'sales', 'safety']
        departments = ['IT', 'Executive', 'Operations', 'Finance', 'Logistics', 'Sales', 'Safety', 'HR']
        
        for i, data in enumerate(base_users):
            user = User.objects.create(
                id=USER_UUIDS[i],
                password=make_password('password123'),
                **data
            )
            users.append(user)
        
        extra_users = 2 * self.volume_multiplier
        for i in range(extra_users):
            idx = len(base_users) + i
            first = random.choice(SA_FIRST_NAMES)
            last = random.choice(SA_LAST_NAMES)
            last_clean = last.replace(" ", "").replace("'", "").lower()
            user = User.objects.create(
                id=USER_UUIDS[idx] if idx < len(USER_UUIDS) else str(uuid.uuid4()),
                username=f"{first[0].lower()}{last_clean}{i}",
                email=f"{first.lower()}.{last_clean}{i}@constructos.co.za",
                first_name=first,
                last_name=last,
                role=random.choice(roles),
                department=random.choice(departments),
                password=make_password('password123'),
            )
            users.append(user)
        
        return users

    def create_accounts(self, users):
        self.stdout.write('Creating accounts...')
        industries = ['Construction', 'Real Estate Development', 'General Contractor', 'Commercial Construction', 
                     'Steel Manufacturing', 'Concrete Supply', 'Technology', 'Government', 'Equipment Rental',
                     'Electrical Supply', 'Property Management', 'Residential Development', 'Plumbing Supply',
                     'HVAC Systems', 'Roofing', 'Landscaping', 'Heavy Equipment', 'Safety Equipment']
        tiers = ['Enterprise', 'Mid-Market', 'Strategic', 'Preferred', 'Standard']
        types = ['customer', 'customer', 'customer', 'vendor', 'prospect']
        payment_terms = ['net_15', 'net_30', 'net_45', 'net_60']
        suffixes = ['Inc.', 'LLC', 'Corp', 'LP', 'Co.', 'Group', 'Partners', 'Systems', 'Solutions']
        
        base_count = 12
        total_accounts = base_count * self.volume_multiplier
        self.stdout.write(f'  Generating {total_accounts} accounts...')
        
        accounts = []
        for i in range(total_accounts):
            company_name = fake.company()
            clean_name = ''.join(c for c in company_name if c.isalnum() or c == ' ').strip()
            domain = clean_name.lower().replace(' ', '')[:20]
            
            acct_type = random.choice(types)
            tier = random.choice(tiers)
            revenue = Decimal(random.randint(5, 200)) * Decimal('1000000') if random.random() > 0.1 else None
            
            account = Account.objects.create(
                id=ACCOUNT_UUIDS[i] if i < len(ACCOUNT_UUIDS) else str(uuid.uuid4()),
                name=company_name,
                legal_name=f"{company_name} {random.choice(suffixes)}",
                type=acct_type,
                industry=random.choice(industries),
                tier=tier,
                annual_revenue=revenue,
                employee_count=random.randint(10, 2000),
                payment_terms=random.choice(payment_terms),
                credit_limit=Decimal(random.randint(50, 2000)) * Decimal('1000'),
                account_number=f"ACC-{str(i+1).zfill(5)}",
                website=f"https://www.{domain}.co.za",
                phone=f"+27 {random.choice(['11', '12', '21', '31', '41', '51'])} {random.randint(100, 999)} {random.randint(1000, 9999)}",
                email=f"info@{domain}.co.za",
                status='active',
                currency='ZAR',
                owner=random.choice(users),
            )
            accounts.append(account)
        
        for i in range(2, min(10, len(accounts)), 3):
            accounts[i].parent_account = accounts[i-1]
            accounts[i].save()
        
        return accounts

    def create_contacts(self, accounts, users):
        self.stdout.write('Creating contacts...')
        titles = ['CEO', 'CFO', 'COO', 'VP of Operations', 'Project Director', 'Procurement Manager', 
                 'Construction Manager', 'Site Supervisor', 'Finance Director', 'Purchasing Agent', 
                 'Contract Administrator', 'Safety Director', 'Quality Manager', 'Engineering Manager', 
                 'Estimator', 'Project Manager', 'Superintendent', 'Foreman']
        departments = ['Executive', 'Operations', 'Finance', 'Procurement', 'Engineering', 
                      'Project Management', 'Safety', 'Quality Assurance', 'Administration', 'HR']
        sources = ['Website', 'Referral', 'Trade Show', 'LinkedIn', 'Cold Call', 'Partner', 'Inbound']
        
        contacts = []
        contact_idx = 0
        for account in accounts:
            num_contacts = random.randint(2, 5)
            clean_domain = ''.join(c for c in account.name if c.isalnum())[:15].lower()
            
            for j in range(num_contacts):
                first = random.choice(SA_FIRST_NAMES)
                last = random.choice(SA_LAST_NAMES)
                last_clean = last.replace(" ", "").replace("'", "").lower()
                area_code = random.choice(['11', '12', '21', '31', '41', '51'])
                contact = Contact.objects.create(
                    id=CONTACT_UUIDS[contact_idx] if contact_idx < len(CONTACT_UUIDS) else str(uuid.uuid4()),
                    first_name=first,
                    last_name=last,
                    email=f"{first.lower()}.{last_clean}{contact_idx}@{clean_domain}.co.za",
                    phone=f"+27 {area_code} {random.randint(100, 999)} {random.randint(1000, 9999)}",
                    mobile=f"+27 {random.choice(['60', '61', '62', '63', '64', '65', '66', '67', '68', '69', '71', '72', '73', '74', '76', '78', '79', '81', '82', '83', '84'])} {random.randint(100, 999)} {random.randint(1000, 9999)}",
                    title=random.choice(titles),
                    department=random.choice(departments),
                    account=account,
                    is_primary=(j == 0),
                    preferred_communication=random.choice(['email', 'phone', 'email', 'email']),
                    status='active',
                    source=random.choice(sources),
                    owner=random.choice(users),
                )
                contacts.append(contact)
                contact_idx += 1
        
        self.stdout.write(f'  Generated {len(contacts)} contacts')
        return contacts

    def create_addresses(self, accounts, contacts):
        self.stdout.write('Creating addresses...')
        cities_provinces = [
            ('Johannesburg', 'Gauteng', '2001'), ('Pretoria', 'Gauteng', '0001'), ('Sandton', 'Gauteng', '2196'),
            ('Cape Town', 'Western Cape', '8001'), ('Stellenbosch', 'Western Cape', '7600'), ('Paarl', 'Western Cape', '7646'),
            ('Durban', 'KwaZulu-Natal', '4001'), ('Pietermaritzburg', 'KwaZulu-Natal', '3201'), ('Richards Bay', 'KwaZulu-Natal', '3900'),
            ('Port Elizabeth', 'Eastern Cape', '6001'), ('East London', 'Eastern Cape', '5201'), ('Gqeberha', 'Eastern Cape', '6001'),
            ('Bloemfontein', 'Free State', '9301'), ('Kimberley', 'Northern Cape', '8301'), ('Polokwane', 'Limpopo', '0700'),
            ('Nelspruit', 'Mpumalanga', '1200'), ('Rustenburg', 'North West', '0299'), ('Centurion', 'Gauteng', '0157'),
        ]
        street_names = ['Main Road', 'Jan Smuts Avenue', 'Voortrekker Road', 'Church Street', 'Long Street', 'Rivonia Road', 'Oxford Road', 'Commissioner Street', 'West Street', 'Mandela Drive', 'Beyers Naude Drive', 'William Nicol Drive']
        
        addresses = []
        for account in accounts:
            for addr_type in ['billing', 'shipping']:
                city, province, postal = random.choice(cities_provinces)
                address = Address.objects.create(
                    id=str(uuid.uuid4()),
                    street=f"{random.randint(1, 999)} {random.choice(street_names)}",
                    street2=random.choice([None, 'Suite 100', 'Floor 5', 'Block A', None, None]),
                    city=city,
                    state=province,
                    postal_code=postal,
                    country='South Africa',
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
        companies = ['Sandton Properties', 'Gauteng Construction', 'Cape Skyline Developers', 'Joburg Build Co', 'Pretoria Premier Contractors', 'Durban Innovative Structures', 'Highveld Building Group', 'Table Mountain Construction', 'Soweto Foundation Inc', 'Midrand BuildRight', 'Centurion Elite Developments', 'Waterfall Builders', 'NextGen SA Construction', 'Apex Building Systems SA', 'Melrose Cornerstone Projects', 'Rivonia Alliance Contractors', 'Rosebank Prime Development', 'Bryanston Structural']
        first_names = ['Thabo', 'Sipho', 'Nomvula', 'Lindiwe', 'Pieter', 'Johan', 'Andile', 'Kagiso', 'Mpho', 'Lerato', 'Willem', 'Francois', 'Thandiwe', 'Bongani', 'Zanele', 'Mandla', 'Precious', 'Themba']
        last_names = ['Molefe', 'Naidoo', 'Van der Merwe', 'Botha', 'Pretorius', 'Dlamini', 'Mthembu', 'Khumalo', 'Ndlovu', 'Zulu', 'Swanepoel', 'Coetzee', 'Mokoena', 'Mahlangu', 'Sithole', 'Mabaso', 'Pillay', 'Govender']
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
                email=f"{first.lower()}.{last.lower()}@{company.lower().replace(' ', '')}.co.za",
                phone=f"+27 {random.choice(['11', '12', '21', '31'])} {random.randint(100,999)} {random.randint(1000,9999)}",
                company=company,
                title=random.choice(['Owner', 'Managing Director', 'VP Operations', 'Director', 'Manager', 'Procurement Lead']),
                source=random.choice(sources),
                status=random.choice(statuses),
                rating=random.choice(ratings),
                estimated_value=Decimal(random.randint(500000, 50000000)),
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
            {'name': 'Johannesburg Main Distribution Centre', 'code': 'WH-JHB', 'address': '150 Industrial Road, Isando', 'city': 'Johannesburg', 'country': 'South Africa', 'capacity': 50000},
            {'name': 'Cape Town Storage Facility', 'code': 'WH-CPT', 'address': '28 Paarden Eiland Road', 'city': 'Cape Town', 'country': 'South Africa', 'capacity': 35000},
            {'name': 'Durban Harbour Depot', 'code': 'WH-DBN', 'address': '45 Maydon Wharf Road', 'city': 'Durban', 'country': 'South Africa', 'capacity': 25000},
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
        categories = ['Structural Steel', 'Concrete', 'Reinforcement', 'Lumber', 'Electrical', 
                     'Plumbing', 'HVAC', 'Insulation', 'Drywall', 'Hardware', 'Safety Equipment',
                     'Tools', 'Formwork', 'Waterproofing', 'Equipment Rental', 'Professional Services',
                     'Windows & Doors', 'Roofing', 'Flooring', 'Paint & Coatings']
        units = ['linear_foot', 'cubic_yard', 'ton', 'board_foot', 'sheet', 'foot', 'each', 
                'bag', 'square_foot', 'box', 'day', 'hour', 'gallon', 'roll']
        
        base_products = [
            {'sku': 'STL-BEAM-W8X31', 'name': 'Steel Wide Flange Beam W8x31', 'category': 'Structural Steel', 'unit': 'linear_foot', 'unit_price': Decimal('45.00'), 'cost_price': Decimal('32.00')},
            {'sku': 'CON-RMX-4000PSI', 'name': 'Ready-Mix Concrete 4000 PSI', 'category': 'Concrete', 'unit': 'cubic_yard', 'unit_price': Decimal('145.00'), 'cost_price': Decimal('98.00')},
            {'sku': 'RBR-GR60-4', 'name': 'Rebar Grade 60 #4', 'category': 'Reinforcement', 'unit': 'ton', 'unit_price': Decimal('1150.00'), 'cost_price': Decimal('820.00')},
            {'sku': 'LUM-2X4-SPF', 'name': 'Lumber 2x4 SPF Stud Grade', 'category': 'Lumber', 'unit': 'board_foot', 'unit_price': Decimal('4.50'), 'cost_price': Decimal('2.80')},
            {'sku': 'ELC-WIRE-12AWG', 'name': 'Electrical Wire 12 AWG THHN', 'category': 'Electrical', 'unit': 'foot', 'unit_price': Decimal('0.85'), 'cost_price': Decimal('0.55')},
        ]
        
        base_count = 30
        total_products = base_count * self.volume_multiplier
        self.stdout.write(f'  Generating {total_products} products...')
        
        sku_prefixes = ['STL', 'CON', 'RBR', 'LUM', 'ELC', 'PLB', 'HVC', 'INS', 'DRY', 'HRD', 
                       'SAF', 'TOL', 'FRM', 'WTR', 'RNT', 'SVC', 'WIN', 'DOR', 'ROF', 'FLR']
        
        products = []
        for i in range(total_products):
            category = random.choice(categories)
            prefix = random.choice(sku_prefixes)
            unit_price = Decimal(random.randint(1, 2500)) + Decimal(random.randint(0, 99)) / 100
            cost_price = unit_price * Decimal('0.65')
            
            product = Product.objects.create(
                id=PRODUCT_UUIDS[i] if i < len(PRODUCT_UUIDS) else str(uuid.uuid4()),
                sku=f"{prefix}-{str(i+1).zfill(5)}",
                name=f"{category} Product {fake.word().title()} {i+1}",
                description=f"High quality {category.lower()} product for construction projects",
                category=category,
                unit=random.choice(units),
                unit_price=unit_price,
                cost_price=cost_price,
                reorder_level=random.randint(10, 500),
                reorder_quantity=random.randint(50, 2000),
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
                min_qty = max(10, int(product.reorder_level * 0.5))
                max_qty = max(min_qty + 100, int(product.reorder_quantity * 1.2))
                qty = random.randint(min_qty, max_qty)
                reserved = random.randint(0, max(1, int(qty * 0.3)))
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
            {'first_name': 'Thabo', 'last_name': 'Molefe', 'department': 'Operations', 'position': 'Site Superintendent', 'salary': Decimal('850000')},
            {'first_name': 'Lindiwe', 'last_name': 'Pretorius', 'department': 'Finance', 'position': 'Controller', 'salary': Decimal('1150000')},
            {'first_name': 'Johan', 'last_name': 'Van der Merwe', 'department': 'Operations', 'position': 'Project Engineer', 'salary': Decimal('720000')},
            {'first_name': 'Nomvula', 'last_name': 'Khumalo', 'department': 'Safety', 'position': 'Safety Manager', 'salary': Decimal('780000')},
            {'first_name': 'Sipho', 'last_name': 'Dlamini', 'department': 'Operations', 'position': 'Crane Operator', 'salary': Decimal('480000')},
            {'first_name': 'Annemarie', 'last_name': 'Botha', 'department': 'HR', 'position': 'HR Manager', 'salary': Decimal('720000')},
            {'first_name': 'Pieter', 'last_name': 'Swanepoel', 'department': 'Logistics', 'position': 'Warehouse Supervisor', 'salary': Decimal('520000')},
            {'first_name': 'Zanele', 'last_name': 'Mthembu', 'department': 'Engineering', 'position': 'Structural Engineer', 'salary': Decimal('920000')},
            {'first_name': 'Bongani', 'last_name': 'Ndlovu', 'department': 'Operations', 'position': 'Foreman', 'salary': Decimal('480000')},
            {'first_name': 'Priya', 'last_name': 'Naidoo', 'department': 'Procurement', 'position': 'Purchasing Manager', 'salary': Decimal('650000')},
            {'first_name': 'Andile', 'last_name': 'Zulu', 'department': 'Operations', 'position': 'Equipment Operator', 'salary': Decimal('420000')},
            {'first_name': 'Mpho', 'last_name': 'Mokoena', 'department': 'Quality', 'position': 'QA Inspector', 'salary': Decimal('480000')},
            {'first_name': 'Francois', 'last_name': 'Coetzee', 'department': 'Operations', 'position': 'Carpenter Lead', 'salary': Decimal('450000')},
            {'first_name': 'Lerato', 'last_name': 'Sithole', 'department': 'Administration', 'position': 'Office Manager', 'salary': Decimal('420000')},
            {'first_name': 'Willem', 'last_name': 'Jansen', 'department': 'Operations', 'position': 'Electrician', 'salary': Decimal('520000')},
        ]
        
        employees = []
        sa_cities = ['Johannesburg', 'Pretoria', 'Sandton', 'Centurion', 'Midrand', 'Randburg', 'Roodepoort', 'Soweto']
        sa_streets = ['Main Road', 'Jan Smuts Avenue', 'Church Street', 'Rivonia Road', 'Oxford Road', 'Mandela Drive', 'Beyers Naude Drive']
        
        for i, data in enumerate(employees_data):
            last_name_clean = data['last_name'].lower().replace(" ", "").replace("'", "")
            emp = Employee.objects.create(
                id=str(uuid.uuid4()),
                employee_number=f"EMP-{str(1001 + i)}",
                user=users[i % len(users)] if i < len(users) else None,
                email=f"{data['first_name'].lower()}.{last_name_clean}@constructos.co.za",
                phone=f"+27 {random.choice(['11', '12', '21', '31'])} {random.randint(100,999)} {random.randint(1000,9999)}",
                hire_date=timezone.now() - timedelta(days=random.randint(180, 1800)),
                salary_frequency='monthly',
                status='active',
                address=f"{random.randint(1, 999)} {random.choice(sa_streets)}",
                city=random.choice(sa_cities),
                country='South Africa',
                emergency_contact=f"{random.choice(['Spouse', 'Parent', 'Sibling'])}",
                emergency_phone=f"+27 {random.choice(['60', '61', '62', '71', '72', '73', '82', '83', '84'])} {random.randint(100,999)} {random.randint(1000,9999)}",
                **data
            )
            employees.append(emp)
        return employees

    def create_projects(self, accounts, users):
        self.stdout.write('Creating projects...')
        projects_data = [
            {'name': 'Sandton Office Tower Phase 1', 'location': '150 Rivonia Road, Sandton, Gauteng', 'status': 'In Progress', 'progress': 65, 'budget': Decimal('450000000'), 'description': 'Class A office tower development with 32 floors of premium office space and ground-level retail in Sandton CBD.'},
            {'name': 'Waterfall Medical Centre', 'location': '25 Waterfall Drive, Midrand, Gauteng', 'status': 'In Progress', 'progress': 42, 'budget': Decimal('780000000'), 'description': 'State-of-the-art medical facility with emergency department, surgical suites, and patient tower.'},
            {'name': 'Soweto Community Centre', 'location': '500 Vilakazi Street, Soweto, Gauteng', 'status': 'Planning', 'progress': 15, 'budget': Decimal('120000000'), 'description': 'Public community centre with gymnasium, meeting rooms, and outdoor recreational facilities.'},
            {'name': 'Cape Town Tech Campus Building B', 'location': '200 Techno Park Drive, Stellenbosch, Western Cape', 'status': 'In Progress', 'progress': 78, 'budget': Decimal('320000000'), 'description': 'Second phase of technology campus expansion with open floor plan and collaboration spaces.'},
            {'name': 'Camps Bay Luxury Residences', 'location': '80 Victoria Road, Camps Bay, Cape Town', 'status': 'Completed', 'progress': 100, 'budget': Decimal('280000000'), 'description': 'High-end residential development with 45 luxury apartment units and premium amenities with ocean views.'},
            {'name': 'Durban Logistics Hub', 'location': '15 Maydon Wharf Road, Durban, KwaZulu-Natal', 'status': 'In Progress', 'progress': 55, 'budget': Decimal('180000000'), 'description': 'Modern logistics facility with automated storage systems and loading dock infrastructure near Durban harbour.'},
            {'name': 'OR Tambo Terminal Renovation', 'location': 'OR Tambo International Airport, Kempton Park, Gauteng', 'status': 'On Hold', 'progress': 25, 'budget': Decimal('950000000'), 'description': 'Comprehensive terminal modernization including expanded gates and enhanced passenger experience.'},
            {'name': 'V&A Waterfront Hotel Development', 'location': '100 Dock Road, V&A Waterfront, Cape Town', 'status': 'Planning', 'progress': 8, 'budget': Decimal('650000000'), 'description': 'Boutique hotel with 250 rooms, rooftop restaurant, and conference facilities overlooking Table Mountain.'},
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
        
        locations = ['Sandton CBD Site', 'Waterfall Medical Centre', 'Stellenbosch Tech Campus', 'Johannesburg Main Warehouse', 'Cape Town Yard', 'Durban Harbour Depot']
        
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
        inspection_types = ['Daily Walkthrough', 'Weekly Safety Audit', 'Monthly Compliance Review', 'DoL Inspection', 'Equipment Safety Check', 'Fire Safety Inspection', 'Fall Protection Audit']
        inspectors = ['Nomvula Khumalo', 'Pieter Jansen', 'Zanele Mthembu', 'Johan Botha', 'Priya Naidoo']
        
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
        authors = ['Thabo Botha', 'Sibongile Naidoo', 'Johan Van der Merwe', 'Lindiwe Pretorius', 'David Swanepoel']
        
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
