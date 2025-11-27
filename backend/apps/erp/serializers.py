from rest_framework import serializers
from .models import (
    Warehouse, Product, StockItem, Invoice, InvoiceLineItem, Payment,
    GeneralLedgerEntry, Employee, PayrollRecord, LeaveRequest,
    SalesOrder, SalesOrderLineItem, PurchaseOrder, PurchaseOrderLineItem
)


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class StockItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockItem
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = '__all__'
        read_only_fields = ['id', 'invoice_number', 'created_at', 'updated_at']


class InvoiceLineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceLineItem
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['id', 'payment_number', 'created_at', 'updated_at']


class GeneralLedgerEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneralLedgerEntry
        fields = '__all__'
        read_only_fields = ['id', 'entry_number', 'created_at']


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'
        read_only_fields = ['id', 'employee_number', 'created_at', 'updated_at']


class PayrollRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollRecord
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class LeaveRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'approved_at']


class SalesOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesOrder
        fields = '__all__'
        read_only_fields = ['id', 'order_number', 'created_at', 'updated_at']


class SalesOrderLineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesOrderLineItem
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class PurchaseOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrder
        fields = '__all__'
        read_only_fields = ['id', 'order_number', 'created_at', 'updated_at', 'approved_at']


class PurchaseOrderLineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrderLineItem
        fields = '__all__'
        read_only_fields = ['id', 'created_at']
