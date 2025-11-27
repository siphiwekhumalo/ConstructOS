import pytest
import uuid
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from backend.apps.core.models import User, Event, AuditLog, Favorite
from backend.apps.crm.models import Account, Contact, Address, Lead, Opportunity, Ticket
from backend.apps.erp.models import (
    Warehouse, Product, StockItem, Invoice, InvoiceLineItem,
    Payment, Employee, SalesOrder, PurchaseOrder
)
from backend.apps.construction.models import Project, Transaction, Equipment, SafetyInspection


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
@pytest.mark.integration
class TestCrmErpIntegration:
    """
    Integration tests for CRM-ERP data flow.
    Tests the Account entity as the central bridge between CRM and ERP.
    """
    
    def test_lead_conversion_to_account_and_contact(self, api_client):
        lead = Lead.objects.create(
            id=str(uuid.uuid4()),
            first_name='Integration',
            last_name='Lead',
            email='integration.lead@example.com',
            phone='+27 82 555 1234',
            company='Test Conversion Company',
            title='Director',
            source='website',
            status='new',
            estimated_value=Decimal('1000000.00'),
        )
        
        response = api_client.post(f'/api/v1/leads/{lead.id}/convert/')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        account_id = data['account_id']
        contact_id = data['contact_id']
        
        account = Account.objects.get(id=account_id)
        assert account.name == 'Test Conversion Company'
        assert account.type == 'customer'
        assert account.status == 'active'
        
        contact = Contact.objects.get(id=contact_id)
        assert contact.first_name == 'Integration'
        assert contact.last_name == 'Lead'
        assert contact.account == account
        
        lead.refresh_from_db()
        assert lead.status == 'converted'
        assert lead.converted_account == account
        assert lead.converted_contact == contact
    
    def test_account_with_invoices_and_payments(self, create_account, create_contact):
        account = create_account(
            name='Payment Test Company',
            payment_terms='net_30',
            credit_limit=Decimal('1000000.00'),
        )
        contact = create_contact(account=account)
        
        invoice = Invoice.objects.create(
            id=str(uuid.uuid4()),
            invoice_number='INV-INT-001',
            account=account,
            contact=contact,
            status='sent',
            due_date=timezone.now() + timedelta(days=30),
            subtotal=Decimal('100000.00'),
            tax_amount=Decimal('15000.00'),
            total_amount=Decimal('115000.00'),
            currency='ZAR',
        )
        
        payment = Payment.objects.create(
            id=str(uuid.uuid4()),
            payment_number='PAY-INT-001',
            invoice=invoice,
            account=account,
            amount=Decimal('50000.00'),
            method='bank_transfer',
            status='completed',
            currency='ZAR',
        )
        
        invoice.paid_amount = payment.amount
        invoice.save()
        
        invoice.refresh_from_db()
        outstanding = invoice.total_amount - invoice.paid_amount
        assert outstanding == Decimal('65000.00')
    
    def test_account_related_data_endpoint(self, api_client, create_account, create_contact):
        account = create_account(name='Related Data Test')
        contact = create_contact(account=account, is_primary=True)
        
        Ticket.objects.create(
            id=str(uuid.uuid4()),
            ticket_number='TKT-REL-001',
            subject='Test Ticket',
            status='open',
            priority='high',
            account=account,
            contact=contact,
        )
        
        Invoice.objects.create(
            id=str(uuid.uuid4()),
            invoice_number='INV-REL-001',
            account=account,
            contact=contact,
            status='sent',
            due_date=timezone.now() + timedelta(days=30),
            subtotal=Decimal('50000.00'),
            total_amount=Decimal('57500.00'),
        )
        
        response = api_client.get(f'/api/v1/accounts/{account.id}/related/')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data['open_tickets_count'] == 1
        assert len(data['open_tickets']) == 1
        assert len(data['recent_invoices']) == 1
        assert len(data['contacts']) == 1
        assert data['contacts'][0]['is_primary'] == True


@pytest.mark.django_db
@pytest.mark.integration
class TestDomainEventsSync:
    """
    Integration tests for domain event emission on model changes.
    """
    
    def test_account_created_event(self, account_data):
        initial_event_count = Event.objects.filter(type='account.created').count()
        
        account = Account.objects.create(**account_data)
        
        events = Event.objects.filter(type='account.created')
        assert events.count() > initial_event_count
        
        latest_event = events.order_by('-created_at').first()
        assert 'Account' in latest_event.payload
        assert str(account.id) in latest_event.payload
    
    def test_account_updated_event(self, account_data):
        account = Account.objects.create(**account_data)
        initial_event_count = Event.objects.filter(type='account.updated').count()
        
        account.name = 'Updated Company Name'
        account.save()
        
        events = Event.objects.filter(type='account.updated')
        assert events.count() > initial_event_count
    
    def test_contact_created_event(self, contact_data, create_account):
        account = create_account()
        contact_data['account'] = account
        initial_event_count = Event.objects.filter(type='contact.created').count()
        
        contact = Contact.objects.create(**contact_data)
        
        events = Event.objects.filter(type='contact.created')
        assert events.count() > initial_event_count


@pytest.mark.django_db
@pytest.mark.integration
class TestProjectConstructionFlow:
    """
    Integration tests for construction project workflows.
    """
    
    def test_project_with_transactions(self, create_project, create_account):
        account = create_account(name='Project Client')
        project = create_project(
            name='Integration Project',
            budget=Decimal('10000000.00'),
            account=account,
        )
        
        expense = Transaction.objects.create(
            id=str(uuid.uuid4()),
            project=project,
            description='Material purchase',
            amount=Decimal('500000.00'),
            status='completed',
            type='expense',
            category='materials',
        )
        
        income = Transaction.objects.create(
            id=str(uuid.uuid4()),
            project=project,
            description='Client milestone payment',
            amount=Decimal('2000000.00'),
            status='completed',
            type='income',
        )
        
        project_transactions = Transaction.objects.filter(project=project)
        assert project_transactions.count() == 2
        
        total_expenses = sum(
            t.amount for t in project_transactions.filter(type='expense')
        )
        total_income = sum(
            t.amount for t in project_transactions.filter(type='income')
        )
        
        assert total_expenses == Decimal('500000.00')
        assert total_income == Decimal('2000000.00')
    
    def test_project_with_equipment_and_inspections(
        self, create_project, create_warehouse, create_employee
    ):
        project = create_project(name='Site Equipment Project')
        warehouse = create_warehouse()
        employee = create_employee()
        
        equipment = Equipment.objects.create(
            id=str(uuid.uuid4()),
            name='Integration Excavator',
            status='operational',
            location=project.location,
            next_service='2024-12-31',
            warehouse=warehouse,
            assigned_to=employee,
        )
        
        inspection = SafetyInspection.objects.create(
            id=str(uuid.uuid4()),
            site=project.location,
            type='routine',
            status='completed',
            inspector=f'{employee.first_name} {employee.last_name}',
            project=project,
            findings='All equipment operating within safety parameters',
        )
        
        assert inspection.project == project
        assert equipment.warehouse == warehouse
        assert equipment.assigned_to == employee


@pytest.mark.django_db
@pytest.mark.integration
class TestInventoryFlow:
    """
    Integration tests for inventory management workflows.
    """
    
    def test_product_stock_management(self, create_product, create_warehouse):
        product = create_product(
            name='Steel Beams',
            sku='STEEL-INT-001',
            unit_price=Decimal('5000.00'),
            reorder_level=50,
        )
        warehouse = create_warehouse(name='Integration Warehouse')
        
        stock = StockItem.objects.create(
            id=str(uuid.uuid4()),
            product=product,
            warehouse=warehouse,
            quantity=100,
            reserved_quantity=20,
            available_quantity=80,
            location='Aisle A, Bay 1',
        )
        
        stock.refresh_from_db()
        assert stock.quantity == 100
        assert stock.available_quantity == 80
        
        stock.reserved_quantity = 50
        stock.available_quantity = stock.quantity - stock.reserved_quantity
        stock.save()
        
        stock.refresh_from_db()
        assert stock.available_quantity == 50
    
    def test_purchase_order_to_stock(self, create_account, create_warehouse, create_product):
        supplier = create_account(type='vendor', name='Material Supplier')
        warehouse = create_warehouse()
        product = create_product()
        
        po = PurchaseOrder.objects.create(
            id=str(uuid.uuid4()),
            order_number='PO-INT-001',
            supplier=supplier,
            warehouse=warehouse,
            status='approved',
            subtotal=Decimal('500000.00'),
            total_amount=Decimal('575000.00'),
        )
        
        existing_stock = StockItem.objects.filter(
            product=product, warehouse=warehouse
        ).first()
        
        if not existing_stock:
            existing_stock = StockItem.objects.create(
                id=str(uuid.uuid4()),
                product=product,
                warehouse=warehouse,
                quantity=0,
                available_quantity=0,
            )
        
        received_quantity = 100
        existing_stock.quantity += received_quantity
        existing_stock.available_quantity += received_quantity
        existing_stock.save()
        
        existing_stock.refresh_from_db()
        assert existing_stock.quantity >= received_quantity


@pytest.mark.django_db
@pytest.mark.integration
class TestSalesFlow:
    """
    Integration tests for sales order to invoice workflow.
    """
    
    def test_sales_order_to_invoice(self, create_account, create_contact, create_product):
        account = create_account(name='Sales Customer')
        contact = create_contact(account=account)
        product = create_product()
        
        sales_order = SalesOrder.objects.create(
            id=str(uuid.uuid4()),
            order_number='SO-INT-001',
            account=account,
            contact=contact,
            status='confirmed',
            subtotal=Decimal('100000.00'),
            tax_amount=Decimal('15000.00'),
            total_amount=Decimal('115000.00'),
            currency='ZAR',
        )
        
        invoice = Invoice.objects.create(
            id=str(uuid.uuid4()),
            invoice_number='INV-FROM-SO-001',
            account=account,
            contact=contact,
            status='draft',
            due_date=timezone.now() + timedelta(days=30),
            subtotal=sales_order.subtotal,
            tax_amount=sales_order.tax_amount,
            total_amount=sales_order.total_amount,
            currency='ZAR',
        )
        
        assert invoice.total_amount == sales_order.total_amount
        assert invoice.account == sales_order.account


@pytest.mark.django_db
@pytest.mark.integration
class TestFavoritesSystem:
    """
    Integration tests for the favorites system.
    """
    
    def test_favorite_project_workflow(self, api_client, create_user, create_project):
        user = create_user()
        project = create_project(name='Favorite Project')
        
        favorite_data = {
            'user': user.id,
            'entity_type': 'project',
            'entity_id': project.id,
            'entity_title': project.name,
            'entity_subtitle': project.location,
        }
        
        response = api_client.post('/api/v1/favorites/', favorite_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        
        response = api_client.get('/api/v1/favorites/', {'user_id': user.id})
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data['results']) == 1
        assert data['results'][0]['entity_type'] == 'project'
    
    def test_favorite_account_workflow(self, api_client, create_user, create_account):
        user = create_user()
        account = create_account(name='Favorite Account')
        
        favorite = Favorite.objects.create(
            id=str(uuid.uuid4()),
            user=user,
            entity_type='account',
            entity_id=account.id,
            entity_title=account.name,
            entity_subtitle=account.industry,
        )
        
        response = api_client.delete(f'/api/v1/favorites/{favorite.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        assert Favorite.objects.filter(id=favorite.id).count() == 0


@pytest.mark.django_db
@pytest.mark.integration
class TestUnifiedSearchIntegration:
    """
    Integration tests for the unified search functionality.
    """
    
    def test_search_across_multiple_entities(
        self, api_client, create_account, create_contact, create_product
    ):
        account = create_account(name='Search Test Company')
        contact = create_contact(
            account=account,
            first_name='Search',
            last_name='User'
        )
        product = create_product(name='Search Product')
        
        Ticket.objects.create(
            id=str(uuid.uuid4()),
            ticket_number='TKT-SEARCH-001',
            subject='Search Related Issue',
            status='open',
            account=account,
        )
        
        response = api_client.get('/api/v1/search/', {'q': 'Search'})
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data['total'] > 0
        
        entity_types = set()
        if data['contacts']:
            entity_types.add('contact')
        if data['products']:
            entity_types.add('product')
        if data['tickets']:
            entity_types.add('ticket')
        
        assert len(entity_types) >= 2


@pytest.mark.django_db
@pytest.mark.integration
class TestHRPayrollFlow:
    """
    Integration tests for HR and payroll workflows.
    """
    
    def test_employee_payroll_cycle(self, create_user, create_employee):
        user = create_user()
        employee = create_employee(
            user=user,
            salary=Decimal('60000.00'),
            department='Engineering',
        )
        
        from backend.apps.erp.models import PayrollRecord
        payroll = PayrollRecord.objects.create(
            id=str(uuid.uuid4()),
            employee=employee,
            period_start=timezone.now() - timedelta(days=30),
            period_end=timezone.now(),
            base_salary=employee.salary,
            overtime=Decimal('5000.00'),
            bonus=Decimal('2000.00'),
            deductions=Decimal('1500.00'),
            tax_amount=Decimal('15000.00'),
            net_pay=Decimal('50500.00'),
            status='pending',
        )
        
        payroll.status = 'approved'
        payroll.save()
        
        payroll.status = 'paid'
        payroll.paid_date = timezone.now()
        payroll.save()
        
        payroll.refresh_from_db()
        assert payroll.status == 'paid'
        assert payroll.paid_date is not None
    
    def test_employee_leave_request(self, create_user, create_employee):
        manager = create_user(role='hr')
        employee = create_employee()
        
        from backend.apps.erp.models import LeaveRequest
        leave = LeaveRequest.objects.create(
            id=str(uuid.uuid4()),
            employee=employee,
            type='annual',
            start_date=timezone.now() + timedelta(days=7),
            end_date=timezone.now() + timedelta(days=14),
            total_days=Decimal('7.0'),
            reason='Family vacation',
            status='pending',
        )
        
        leave.status = 'approved'
        leave.approved_by = manager
        leave.approved_at = timezone.now()
        leave.save()
        
        leave.refresh_from_db()
        assert leave.status == 'approved'
        assert leave.approved_by == manager


@pytest.mark.django_db
@pytest.mark.integration
class TestDashboardData:
    """
    Integration tests for dashboard data aggregation.
    """
    
    def test_dashboard_aggregates_data(
        self, api_client, create_project, create_account, create_employee
    ):
        project = create_project(status='Active', budget=Decimal('5000000.00'))
        account = create_account()
        employee = create_employee()
        
        from backend.apps.crm.models import Client
        Client.objects.create(
            id=str(uuid.uuid4()),
            name='Dashboard Test Client',
            company='Test Co',
            role='Director',
            email='client@test.com',
            phone='+27 11 111 1111',
            status='active',
            avatar='',
            account=account,
        )
        
        Transaction.objects.create(
            id=str(uuid.uuid4()),
            project=project,
            description='Dashboard expense',
            amount=Decimal('100000.00'),
            status='completed',
        )
        
        response = api_client.get('/api/v1/dashboard/')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data['projects']['total'] >= 1
        assert data['clients']['total'] >= 1
        assert data['employees']['total'] >= 1
        assert data['financial']['totalExpenses'] >= 100000
