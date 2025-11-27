import pytest
import uuid
from decimal import Decimal
from datetime import timedelta
from rest_framework import status
from rest_framework.test import APIClient
from django.utils import timezone
from backend.apps.erp.models import (
    Warehouse, Product, StockItem, Invoice, Payment,
    Employee, PayrollRecord, SalesOrder, PurchaseOrder
)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestWarehouseViewSet:
    
    def test_list_warehouses(self, api_client, create_warehouse):
        warehouse1 = create_warehouse(name='Warehouse JHB')
        warehouse2 = create_warehouse(name='Warehouse CPT')
        
        response = api_client.get('/api/v1/warehouses/')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'results' in data
        assert len(data['results']) >= 2
    
    def test_create_warehouse(self, api_client):
        warehouse_data = {
            'name': 'New Distribution Center',
            'code': 'DC-JHB-01',
            'address': '100 Industrial Road',
            'city': 'Johannesburg',
            'country': 'South Africa',
            'capacity': 15000,
        }
        response = api_client.post('/api/v1/warehouses/', warehouse_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data['name'] == 'New Distribution Center'
    
    def test_get_warehouse_detail(self, api_client, create_warehouse):
        warehouse = create_warehouse(name='Detail Warehouse')
        
        response = api_client.get(f'/api/v1/warehouses/{warehouse.id}/')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['name'] == 'Detail Warehouse'


@pytest.mark.django_db
class TestProductViewSet:
    
    def test_list_products(self, api_client, create_product):
        product1 = create_product(name='Product A')
        product2 = create_product(name='Product B')
        
        response = api_client.get('/api/v1/products/')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'results' in data
        assert len(data['results']) >= 2
    
    def test_create_product(self, api_client):
        product_data = {
            'sku': 'BRICK-RED-001',
            'name': 'Red Clay Bricks',
            'description': 'Premium quality red clay bricks',
            'category': 'Building Materials',
            'unit_price': '8.50',
            'cost_price': '5.25',
            'unit': 'each',
            'reorder_level': 1000,
            'reorder_quantity': 5000,
        }
        response = api_client.post('/api/v1/products/', product_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data['name'] == 'Red Clay Bricks'
    
    def test_product_lookup(self, api_client, create_product):
        product = create_product(name='Searchable Product', sku='SEARCH-001')
        
        response = api_client.get('/api/v1/products/lookup/', {'term': 'Search'})
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestInvoiceViewSet:
    
    def test_list_invoices(self, api_client, invoice_data, create_account):
        account = create_account()
        invoice_data['account'] = account
        Invoice.objects.create(**invoice_data)
        
        response = api_client.get('/api/v1/invoices/')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'results' in data
    
    def test_create_invoice(self, api_client, create_account):
        account = create_account()
        invoice_data = {
            'invoice_number': f'INV-{uuid.uuid4().hex[:8]}',
            'account': account.id,
            'status': 'draft',
            'due_date': (timezone.now() + timedelta(days=30)).isoformat(),
            'subtotal': '100000.00',
            'tax_amount': '15000.00',
            'total_amount': '115000.00',
            'currency': 'ZAR',
        }
        response = api_client.post('/api/v1/invoices/', invoice_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data['currency'] == 'ZAR'
    
    def test_update_invoice_status(self, api_client, invoice_data, create_account):
        account = create_account()
        invoice_data['account'] = account
        invoice = Invoice.objects.create(**invoice_data)
        
        response = api_client.patch(
            f'/api/v1/invoices/{invoice.id}/',
            {'status': 'sent'},
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['status'] == 'sent'


@pytest.mark.django_db
class TestPaymentViewSet:
    
    def test_list_payments(self, api_client, create_account):
        account = create_account()
        Payment.objects.create(
            id=str(uuid.uuid4()),
            payment_number='PAY-001',
            account=account,
            amount=Decimal('50000.00'),
            method='bank_transfer',
            status='completed',
        )
        
        response = api_client.get('/api/v1/payments/')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'results' in data
    
    def test_create_payment(self, api_client, create_account):
        account = create_account()
        payment_data = {
            'payment_number': f'PAY-{uuid.uuid4().hex[:8]}',
            'account': account.id,
            'amount': '25000.00',
            'method': 'eft',
            'currency': 'ZAR',
            'reference': 'Client payment for invoice INV-001',
        }
        response = api_client.post('/api/v1/payments/', payment_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data['currency'] == 'ZAR'


@pytest.mark.django_db
class TestEmployeeViewSet:
    
    def test_list_employees(self, api_client, create_employee):
        employee1 = create_employee(first_name='Employee1')
        employee2 = create_employee(first_name='Employee2')
        
        response = api_client.get('/api/v1/employees/')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'results' in data
        assert len(data['results']) >= 2
    
    def test_create_employee(self, api_client):
        employee_data = {
            'employee_number': f'EMP-{uuid.uuid4().hex[:6]}',
            'first_name': 'Nomsa',
            'last_name': 'Dlamini',
            'email': 'nomsa.dlamini@example.co.za',
            'phone': '+27 82 555 1234',
            'department': 'Construction',
            'position': 'Site Engineer',
            'hire_date': timezone.now().isoformat(),
            'salary': '55000.00',
            'status': 'active',
        }
        response = api_client.post('/api/v1/employees/', employee_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data['first_name'] == 'Nomsa'
    
    def test_filter_employees_by_department(self, api_client, create_employee):
        eng_employee = create_employee(department='Engineering')
        hr_employee = create_employee(department='HR')
        
        response = api_client.get('/api/v1/employees/', {'department': 'Engineering'})
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestPayrollRecordViewSet:
    
    def test_list_payroll_records(self, api_client, create_employee):
        employee = create_employee()
        PayrollRecord.objects.create(
            id=str(uuid.uuid4()),
            employee=employee,
            period_start=timezone.now() - timedelta(days=30),
            period_end=timezone.now(),
            base_salary=Decimal('45000.00'),
            net_pay=Decimal('35000.00'),
            status='paid',
        )
        
        response = api_client.get('/api/v1/payroll/')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'results' in data
    
    def test_create_payroll_record(self, api_client, create_employee):
        employee = create_employee()
        payroll_data = {
            'employee': employee.id,
            'period_start': (timezone.now() - timedelta(days=30)).isoformat(),
            'period_end': timezone.now().isoformat(),
            'base_salary': '45000.00',
            'overtime': '5000.00',
            'bonus': '0.00',
            'deductions': '2000.00',
            'tax_amount': '10000.00',
            'net_pay': '38000.00',
            'status': 'pending',
        }
        response = api_client.post('/api/v1/payroll/', payroll_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
class TestSalesOrderViewSet:
    
    def test_list_sales_orders(self, api_client, create_account):
        account = create_account()
        SalesOrder.objects.create(
            id=str(uuid.uuid4()),
            order_number='SO-001',
            account=account,
            status='confirmed',
            subtotal=Decimal('100000.00'),
            total_amount=Decimal('115000.00'),
        )
        
        response = api_client.get('/api/v1/sales-orders/')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'results' in data
    
    def test_create_sales_order(self, api_client, create_account):
        account = create_account()
        order_data = {
            'order_number': f'SO-{uuid.uuid4().hex[:8]}',
            'account': account.id,
            'status': 'draft',
            'subtotal': '500000.00',
            'tax_amount': '75000.00',
            'total_amount': '575000.00',
            'currency': 'ZAR',
        }
        response = api_client.post('/api/v1/sales-orders/', order_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data['currency'] == 'ZAR'


@pytest.mark.django_db
class TestPurchaseOrderViewSet:
    
    def test_list_purchase_orders(self, api_client, create_account):
        supplier = create_account(type='vendor')
        PurchaseOrder.objects.create(
            id=str(uuid.uuid4()),
            order_number='PO-001',
            supplier=supplier,
            status='approved',
            subtotal=Decimal('200000.00'),
            total_amount=Decimal('230000.00'),
        )
        
        response = api_client.get('/api/v1/purchase-orders/')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'results' in data
    
    def test_create_purchase_order(self, api_client, create_account, create_warehouse):
        supplier = create_account(type='vendor')
        warehouse = create_warehouse()
        order_data = {
            'order_number': f'PO-{uuid.uuid4().hex[:8]}',
            'supplier': supplier.id,
            'warehouse': warehouse.id,
            'status': 'draft',
            'subtotal': '300000.00',
            'tax_amount': '45000.00',
            'total_amount': '345000.00',
            'currency': 'ZAR',
        }
        response = api_client.post('/api/v1/purchase-orders/', order_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data['currency'] == 'ZAR'
