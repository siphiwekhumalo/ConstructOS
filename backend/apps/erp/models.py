import uuid
from django.db import models
from backend.apps.core.models import User
from backend.apps.crm.models import Account, Contact, Opportunity


class Warehouse(models.Model):
    id = models.CharField(max_length=255, primary_key=True, default=uuid.uuid4)
    name = models.TextField()
    code = models.TextField(unique=True)
    address = models.TextField(null=True, blank=True)
    city = models.TextField(null=True, blank=True)
    country = models.TextField(null=True, blank=True)
    capacity = models.IntegerField(null=True, blank=True)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, db_column='manager_id')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'warehouses'


class Product(models.Model):
    id = models.CharField(max_length=255, primary_key=True, default=uuid.uuid4)
    sku = models.TextField(unique=True)
    name = models.TextField()
    description = models.TextField(null=True, blank=True)
    category = models.TextField(null=True, blank=True)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    unit = models.TextField(default='each')
    reorder_level = models.IntegerField(default=10)
    reorder_quantity = models.IntegerField(default=50)
    is_active = models.BooleanField(default=True)
    image_url = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'


class StockItem(models.Model):
    id = models.CharField(max_length=255, primary_key=True, default=uuid.uuid4)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_column='product_id')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, db_column='warehouse_id')
    quantity = models.IntegerField(default=0)
    reserved_quantity = models.IntegerField(default=0)
    available_quantity = models.IntegerField(default=0)
    location = models.TextField(null=True, blank=True)
    last_counted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'stock_items'


class Invoice(models.Model):
    id = models.CharField(max_length=255, primary_key=True, default=uuid.uuid4)
    invoice_number = models.TextField(unique=True)
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, db_column='account_id')
    contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True, db_column='contact_id')
    status = models.TextField(default='draft')
    issue_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    subtotal = models.DecimalField(max_digits=15, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    currency = models.TextField(default='USD')
    notes = models.TextField(null=True, blank=True)
    terms = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'invoices'


class InvoiceLineItem(models.Model):
    id = models.CharField(max_length=255, primary_key=True, default=uuid.uuid4)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, db_column='invoice_id')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, db_column='product_id')
    description = models.TextField()
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'invoice_line_items'


class Payment(models.Model):
    id = models.CharField(max_length=255, primary_key=True, default=uuid.uuid4)
    payment_number = models.TextField(unique=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, db_column='invoice_id')
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, db_column='account_id')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.TextField(default='USD')
    method = models.TextField()
    status = models.TextField(default='pending')
    payment_date = models.DateTimeField(auto_now_add=True)
    reference = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payments'


class GeneralLedgerEntry(models.Model):
    id = models.CharField(max_length=255, primary_key=True, default=uuid.uuid4)
    entry_number = models.TextField(unique=True)
    date = models.DateTimeField(auto_now_add=True)
    account_code = models.TextField()
    account_name = models.TextField()
    description = models.TextField(null=True, blank=True)
    debit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    reference = models.TextField(null=True, blank=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, db_column='invoice_id')
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, db_column='payment_id')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'general_ledger_entries'


class Employee(models.Model):
    id = models.CharField(max_length=255, primary_key=True, default=uuid.uuid4)
    employee_number = models.TextField(unique=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, db_column='user_id')
    first_name = models.TextField()
    last_name = models.TextField()
    email = models.TextField()
    phone = models.TextField(null=True, blank=True)
    department = models.TextField(null=True, blank=True)
    position = models.TextField(null=True, blank=True)
    manager_id = models.CharField(max_length=255, null=True, blank=True)
    hire_date = models.DateTimeField()
    termination_date = models.DateTimeField(null=True, blank=True)
    salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    salary_frequency = models.TextField(default='monthly')
    status = models.TextField(default='active')
    address = models.TextField(null=True, blank=True)
    city = models.TextField(null=True, blank=True)
    country = models.TextField(null=True, blank=True)
    emergency_contact = models.TextField(null=True, blank=True)
    emergency_phone = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'employees'


class PayrollRecord(models.Model):
    id = models.CharField(max_length=255, primary_key=True, default=uuid.uuid4)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, db_column='employee_id')
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    base_salary = models.DecimalField(max_digits=12, decimal_places=2)
    overtime = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    bonus = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_pay = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.TextField(default='pending')
    paid_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payroll_records'


class LeaveRequest(models.Model):
    id = models.CharField(max_length=255, primary_key=True, default=uuid.uuid4)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, db_column='employee_id')
    type = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    total_days = models.DecimalField(max_digits=5, decimal_places=1)
    reason = models.TextField(null=True, blank=True)
    status = models.TextField(default='pending')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, db_column='approved_by_id')
    approved_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'leave_requests'


class SalesOrder(models.Model):
    id = models.CharField(max_length=255, primary_key=True, default=uuid.uuid4)
    order_number = models.TextField(unique=True)
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, db_column='account_id')
    contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True, db_column='contact_id')
    opportunity = models.ForeignKey(Opportunity, on_delete=models.SET_NULL, null=True, db_column='opportunity_id')
    status = models.TextField(default='draft')
    order_date = models.DateTimeField(auto_now_add=True)
    delivery_date = models.DateTimeField(null=True, blank=True)
    shipping_address = models.TextField(null=True, blank=True)
    billing_address = models.TextField(null=True, blank=True)
    subtotal = models.DecimalField(max_digits=15, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.TextField(default='USD')
    notes = models.TextField(null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, db_column='owner_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sales_orders'


class SalesOrderLineItem(models.Model):
    id = models.CharField(max_length=255, primary_key=True, default=uuid.uuid4)
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, db_column='sales_order_id')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, db_column='product_id')
    description = models.TextField()
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sales_order_line_items'


class PurchaseOrder(models.Model):
    id = models.CharField(max_length=255, primary_key=True, default=uuid.uuid4)
    order_number = models.TextField(unique=True)
    supplier = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, db_column='supplier_id')
    status = models.TextField(default='draft')
    order_date = models.DateTimeField(auto_now_add=True)
    expected_delivery_date = models.DateTimeField(null=True, blank=True)
    received_date = models.DateTimeField(null=True, blank=True)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True, db_column='warehouse_id')
    subtotal = models.DecimalField(max_digits=15, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.TextField(default='USD')
    notes = models.TextField(null=True, blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, db_column='approved_by_id')
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'purchase_orders'


class PurchaseOrderLineItem(models.Model):
    id = models.CharField(max_length=255, primary_key=True, default=uuid.uuid4)
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, db_column='purchase_order_id')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, db_column='product_id')
    description = models.TextField()
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    received_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'purchase_order_line_items'
