import pytest
from decimal import Decimal
import uuid
from datetime import timedelta
from django.utils import timezone
from backend.apps.erp.models import (
    Warehouse, Product, StockItem, Invoice, InvoiceLineItem,
    Payment, Employee, PayrollRecord, LeaveRequest, SalesOrder, PurchaseOrder
)


@pytest.mark.django_db
class TestWarehouseModel:
    
    def test_create_warehouse(self, warehouse_data, create_user):
        user = create_user()
        warehouse_data['manager'] = user
        warehouse = Warehouse.objects.create(**warehouse_data)
        assert warehouse.name == warehouse_data['name']
        assert warehouse.code == 'JHB-CEN-01'
        assert warehouse.city == 'Johannesburg'
    
    def test_warehouse_unique_code(self, warehouse_data):
        Warehouse.objects.create(**warehouse_data)
        warehouse_data['id'] = str(uuid.uuid4())
        warehouse_data['name'] = 'Another Warehouse'
        with pytest.raises(Exception):
            Warehouse.objects.create(**warehouse_data)
    
    def test_warehouse_default_active_status(self):
        warehouse = Warehouse.objects.create(
            id=str(uuid.uuid4()),
            name='Test Warehouse',
            code=f'WH-{uuid.uuid4().hex[:6]}',
        )
        assert warehouse.is_active == True


@pytest.mark.django_db
class TestProductModel:
    
    def test_create_product(self, product_data):
        product = Product.objects.create(**product_data)
        assert product.name == product_data['name']
        assert product.sku == 'CEMENT-50KG-001'
        assert product.unit_price == Decimal('125.00')
        assert product.cost_price == Decimal('95.00')
    
    def test_product_unique_sku(self, product_data):
        Product.objects.create(**product_data)
        product_data['id'] = str(uuid.uuid4())
        product_data['name'] = 'Another Product'
        with pytest.raises(Exception):
            Product.objects.create(**product_data)
    
    def test_product_profit_margin(self, product_data):
        product = Product.objects.create(**product_data)
        profit_margin = product.unit_price - product.cost_price
        assert profit_margin == Decimal('30.00')
    
    def test_product_reorder_levels(self, product_data):
        product = Product.objects.create(**product_data)
        assert product.reorder_level == 100
        assert product.reorder_quantity == 500


@pytest.mark.django_db
class TestStockItemModel:
    
    def test_create_stock_item(self, create_product, create_warehouse):
        product = create_product()
        warehouse = create_warehouse()
        stock = StockItem.objects.create(
            id=str(uuid.uuid4()),
            product=product,
            warehouse=warehouse,
            quantity=500,
            reserved_quantity=50,
            available_quantity=450,
            location='Aisle A, Shelf 3',
        )
        assert stock.quantity == 500
        assert stock.available_quantity == 450
    
    def test_stock_item_cascade_on_product_delete(self, create_product, create_warehouse):
        product = create_product()
        warehouse = create_warehouse()
        stock = StockItem.objects.create(
            id=str(uuid.uuid4()),
            product=product,
            warehouse=warehouse,
            quantity=100,
        )
        product_id = product.id
        product.delete()
        assert StockItem.objects.filter(product_id=product_id).count() == 0


@pytest.mark.django_db
class TestInvoiceModel:
    
    def test_create_invoice(self, invoice_data, create_account):
        account = create_account()
        invoice_data['account'] = account
        invoice = Invoice.objects.create(**invoice_data)
        assert invoice.invoice_number == 'INV-2024-001'
        assert invoice.total_amount == Decimal('115000.00')
        assert invoice.currency == 'ZAR'
    
    def test_invoice_unique_number(self, invoice_data, create_account):
        account = create_account()
        invoice_data['account'] = account
        Invoice.objects.create(**invoice_data)
        invoice_data['id'] = str(uuid.uuid4())
        with pytest.raises(Exception):
            Invoice.objects.create(**invoice_data)
    
    def test_invoice_payment_tracking(self, invoice_data, create_account):
        account = create_account()
        invoice_data['account'] = account
        invoice_data['paid_amount'] = Decimal('50000.00')
        invoice = Invoice.objects.create(**invoice_data)
        outstanding = invoice.total_amount - invoice.paid_amount
        assert outstanding == Decimal('65000.00')
    
    def test_invoice_status_transitions(self, create_account):
        account = create_account()
        statuses = ['draft', 'sent', 'paid', 'overdue', 'cancelled']
        for status in statuses:
            invoice = Invoice.objects.create(
                id=str(uuid.uuid4()),
                invoice_number=f'INV-{uuid.uuid4().hex[:8]}',
                account=account,
                status=status,
                due_date=timezone.now() + timedelta(days=30),
                subtotal=Decimal('1000.00'),
                total_amount=Decimal('1150.00'),
            )
            assert invoice.status == status


@pytest.mark.django_db
class TestPaymentModel:
    
    def test_create_payment(self, create_account):
        account = create_account()
        payment = Payment.objects.create(
            id=str(uuid.uuid4()),
            payment_number='PAY-2024-001',
            account=account,
            amount=Decimal('50000.00'),
            currency='ZAR',
            method='bank_transfer',
            status='completed',
            reference='EFT Reference 12345',
        )
        assert payment.amount == Decimal('50000.00')
        assert payment.method == 'bank_transfer'
    
    def test_payment_unique_number(self, create_account):
        account = create_account()
        Payment.objects.create(
            id=str(uuid.uuid4()),
            payment_number='PAY-001',
            account=account,
            amount=Decimal('1000.00'),
            method='cash',
        )
        with pytest.raises(Exception):
            Payment.objects.create(
                id=str(uuid.uuid4()),
                payment_number='PAY-001',
                account=account,
                amount=Decimal('2000.00'),
                method='card',
            )
    
    def test_payment_methods(self, create_account):
        account = create_account()
        methods = ['cash', 'bank_transfer', 'credit_card', 'debit_card', 'cheque']
        for method in methods:
            payment = Payment.objects.create(
                id=str(uuid.uuid4()),
                payment_number=f'PAY-{uuid.uuid4().hex[:8]}',
                account=account,
                amount=Decimal('1000.00'),
                method=method,
            )
            assert payment.method == method


@pytest.mark.django_db
class TestEmployeeModel:
    
    def test_create_employee(self, employee_data, create_user):
        user = create_user()
        employee_data['user'] = user
        employee = Employee.objects.create(**employee_data)
        assert employee.first_name == 'Sipho'
        assert employee.last_name == 'Nkosi'
        assert employee.salary == Decimal('45000.00')
    
    def test_employee_unique_number(self, employee_data):
        Employee.objects.create(**employee_data)
        employee_data['id'] = str(uuid.uuid4())
        employee_data['email'] = 'another@example.com'
        with pytest.raises(Exception):
            Employee.objects.create(**employee_data)
    
    def test_employee_status_values(self):
        statuses = ['active', 'on_leave', 'terminated', 'suspended']
        for status in statuses:
            employee = Employee.objects.create(
                id=str(uuid.uuid4()),
                employee_number=f'EMP-{uuid.uuid4().hex[:6]}',
                first_name='Test',
                last_name='Employee',
                email=f'{uuid.uuid4().hex[:8]}@example.com',
                hire_date=timezone.now(),
                status=status,
            )
            assert employee.status == status


@pytest.mark.django_db
class TestPayrollRecordModel:
    
    def test_create_payroll_record(self, create_employee):
        employee = create_employee()
        payroll = PayrollRecord.objects.create(
            id=str(uuid.uuid4()),
            employee=employee,
            period_start=timezone.now() - timedelta(days=30),
            period_end=timezone.now(),
            base_salary=Decimal('45000.00'),
            overtime=Decimal('5000.00'),
            bonus=Decimal('2000.00'),
            deductions=Decimal('3000.00'),
            tax_amount=Decimal('12000.00'),
            net_pay=Decimal('37000.00'),
            status='paid',
        )
        assert payroll.net_pay == Decimal('37000.00')
        assert payroll.status == 'paid'
    
    def test_payroll_calculation(self, create_employee):
        employee = create_employee()
        base_salary = Decimal('45000.00')
        overtime = Decimal('5000.00')
        bonus = Decimal('2000.00')
        deductions = Decimal('3000.00')
        tax_amount = Decimal('12000.00')
        expected_net = base_salary + overtime + bonus - deductions - tax_amount
        
        payroll = PayrollRecord.objects.create(
            id=str(uuid.uuid4()),
            employee=employee,
            period_start=timezone.now() - timedelta(days=30),
            period_end=timezone.now(),
            base_salary=base_salary,
            overtime=overtime,
            bonus=bonus,
            deductions=deductions,
            tax_amount=tax_amount,
            net_pay=expected_net,
        )
        assert payroll.net_pay == expected_net


@pytest.mark.django_db
class TestLeaveRequestModel:
    
    def test_create_leave_request(self, create_employee, create_user):
        employee = create_employee()
        approver = create_user()
        leave = LeaveRequest.objects.create(
            id=str(uuid.uuid4()),
            employee=employee,
            type='annual',
            start_date=timezone.now() + timedelta(days=7),
            end_date=timezone.now() + timedelta(days=14),
            total_days=Decimal('7.0'),
            reason='Family vacation',
            status='approved',
            approved_by=approver,
            approved_at=timezone.now(),
        )
        assert leave.total_days == Decimal('7.0')
        assert leave.status == 'approved'
    
    def test_leave_types(self, create_employee):
        employee = create_employee()
        leave_types = ['annual', 'sick', 'maternity', 'paternity', 'unpaid', 'compassionate']
        for leave_type in leave_types:
            leave = LeaveRequest.objects.create(
                id=str(uuid.uuid4()),
                employee=employee,
                type=leave_type,
                start_date=timezone.now() + timedelta(days=1),
                end_date=timezone.now() + timedelta(days=2),
                total_days=Decimal('1.0'),
            )
            assert leave.type == leave_type
    
    def test_leave_status_workflow(self, create_employee):
        employee = create_employee()
        statuses = ['pending', 'approved', 'rejected', 'cancelled']
        for status in statuses:
            leave = LeaveRequest.objects.create(
                id=str(uuid.uuid4()),
                employee=employee,
                type='annual',
                start_date=timezone.now() + timedelta(days=1),
                end_date=timezone.now() + timedelta(days=3),
                total_days=Decimal('2.0'),
                status=status,
            )
            assert leave.status == status


@pytest.mark.django_db
class TestSalesOrderModel:
    
    def test_create_sales_order(self, create_account):
        account = create_account()
        order = SalesOrder.objects.create(
            id=str(uuid.uuid4()),
            order_number='SO-2024-001',
            account=account,
            status='confirmed',
            subtotal=Decimal('100000.00'),
            tax_amount=Decimal('15000.00'),
            shipping_cost=Decimal('500.00'),
            discount=Decimal('5000.00'),
            total_amount=Decimal('110500.00'),
            currency='ZAR',
        )
        assert order.order_number == 'SO-2024-001'
        assert order.total_amount == Decimal('110500.00')
    
    def test_sales_order_unique_number(self, create_account):
        account = create_account()
        SalesOrder.objects.create(
            id=str(uuid.uuid4()),
            order_number='SO-001',
            account=account,
            subtotal=Decimal('1000.00'),
            total_amount=Decimal('1150.00'),
        )
        with pytest.raises(Exception):
            SalesOrder.objects.create(
                id=str(uuid.uuid4()),
                order_number='SO-001',
                account=account,
                subtotal=Decimal('2000.00'),
                total_amount=Decimal('2300.00'),
            )


@pytest.mark.django_db
class TestPurchaseOrderModel:
    
    def test_create_purchase_order(self, create_account, create_warehouse, create_user):
        supplier = create_account(type='vendor')
        warehouse = create_warehouse()
        approver = create_user()
        order = PurchaseOrder.objects.create(
            id=str(uuid.uuid4()),
            order_number='PO-2024-001',
            supplier=supplier,
            status='approved',
            warehouse=warehouse,
            subtotal=Decimal('500000.00'),
            tax_amount=Decimal('75000.00'),
            shipping_cost=Decimal('2500.00'),
            total_amount=Decimal('577500.00'),
            currency='ZAR',
            approved_by=approver,
            approved_at=timezone.now(),
        )
        assert order.order_number == 'PO-2024-001'
        assert order.supplier.type == 'vendor'
        assert order.total_amount == Decimal('577500.00')
    
    def test_purchase_order_status_workflow(self, create_account):
        supplier = create_account(type='vendor')
        statuses = ['draft', 'pending_approval', 'approved', 'ordered', 'received', 'cancelled']
        for status in statuses:
            order = PurchaseOrder.objects.create(
                id=str(uuid.uuid4()),
                order_number=f'PO-{uuid.uuid4().hex[:8]}',
                supplier=supplier,
                status=status,
                subtotal=Decimal('10000.00'),
                total_amount=Decimal('11500.00'),
            )
            assert order.status == status
