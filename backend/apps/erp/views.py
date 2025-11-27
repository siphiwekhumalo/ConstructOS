import uuid
import random
from django.db import models
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import (
    Warehouse, Product, StockItem, Invoice, InvoiceLineItem, Payment,
    GeneralLedgerEntry, Employee, PayrollRecord, LeaveRequest,
    SalesOrder, SalesOrderLineItem, PurchaseOrder, PurchaseOrderLineItem
)
from .serializers import (
    WarehouseSerializer, ProductSerializer, StockItemSerializer,
    InvoiceSerializer, InvoiceLineItemSerializer, PaymentSerializer,
    GeneralLedgerEntrySerializer, EmployeeSerializer, PayrollRecordSerializer,
    LeaveRequestSerializer, SalesOrderSerializer, SalesOrderLineItemSerializer,
    PurchaseOrderSerializer, PurchaseOrderLineItemSerializer
)


class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all().order_by('-created_at')
    serializer_class = WarehouseSerializer
    filterset_fields = ['is_active']
    search_fields = ['name', 'code', 'city']


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer
    filterset_fields = ['is_active', 'category']
    search_fields = ['name', 'sku', 'description']

    @action(detail=False, methods=['get'])
    def lookup(self, request):
        """
        Lookup products for line item selector.
        Returns product details with stock availability.
        """
        from django.db.models import Sum
        
        term = request.query_params.get('term', '').strip()
        limit = int(request.query_params.get('limit', 10))
        warehouse_id = request.query_params.get('warehouse_id')
        
        if not term or len(term) < 2:
            return Response([])
        
        products = Product.objects.filter(
            is_active=True
        ).filter(
            models.Q(name__icontains=term) |
            models.Q(sku__icontains=term)
        )[:limit]
        
        results = []
        for product in products:
            stock_query = StockItem.objects.filter(product=product)
            if warehouse_id:
                stock_query = stock_query.filter(warehouse_id=warehouse_id)
            
            total_stock = stock_query.aggregate(total=Sum('quantity'))['total'] or 0
            
            in_stock = total_stock > 0
            stock_status = 'in_stock' if total_stock > product.reorder_level else (
                'low_stock' if total_stock > 0 else 'out_of_stock'
            )
            
            results.append({
                'id': product.id,
                'sku': product.sku,
                'name': product.name,
                'description': product.description,
                'category': product.category,
                'unit': product.unit,
                'unit_price': str(product.unit_price),
                'cost_price': str(product.cost_price) if product.cost_price else None,
                'stock': {
                    'quantity': total_stock,
                    'in_stock': in_stock,
                    'status': stock_status,
                    'reorder_level': product.reorder_level,
                }
            })
        
        return Response(results)


class StockItemViewSet(viewsets.ModelViewSet):
    queryset = StockItem.objects.all().order_by('-created_at')
    serializer_class = StockItemSerializer
    filterset_fields = ['product', 'warehouse']


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all().order_by('-created_at')
    serializer_class = InvoiceSerializer
    filterset_fields = ['status', 'account']
    search_fields = ['invoice_number']

    def perform_create(self, serializer):
        invoice_number = f"INV-{random.randint(100000, 999999)}"
        serializer.save(invoice_number=invoice_number)


class InvoiceLineItemViewSet(viewsets.ModelViewSet):
    queryset = InvoiceLineItem.objects.all().order_by('-created_at')
    serializer_class = InvoiceLineItemSerializer
    filterset_fields = ['invoice', 'product']


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all().order_by('-created_at')
    serializer_class = PaymentSerializer
    filterset_fields = ['status', 'method', 'invoice']
    search_fields = ['payment_number', 'reference']

    def perform_create(self, serializer):
        payment_number = f"PAY-{random.randint(100000, 999999)}"
        serializer.save(payment_number=payment_number)


class GeneralLedgerEntryViewSet(viewsets.ModelViewSet):
    queryset = GeneralLedgerEntry.objects.all().order_by('-created_at')
    serializer_class = GeneralLedgerEntrySerializer
    filterset_fields = ['account_code']
    search_fields = ['entry_number', 'description']


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all().order_by('-created_at')
    serializer_class = EmployeeSerializer
    filterset_fields = ['status', 'department']
    search_fields = ['first_name', 'last_name', 'email', 'employee_number']

    def perform_create(self, serializer):
        employee_number = f"EMP-{random.randint(100000, 999999)}"
        serializer.save(employee_number=employee_number)


class PayrollRecordViewSet(viewsets.ModelViewSet):
    queryset = PayrollRecord.objects.all().order_by('-created_at')
    serializer_class = PayrollRecordSerializer
    filterset_fields = ['status', 'employee']


class LeaveRequestViewSet(viewsets.ModelViewSet):
    queryset = LeaveRequest.objects.all().order_by('-created_at')
    serializer_class = LeaveRequestSerializer
    filterset_fields = ['status', 'type', 'employee']

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        leave_request = self.get_object()
        from django.utils import timezone
        leave_request.status = 'approved'
        leave_request.approved_at = timezone.now()
        leave_request.save()
        return Response({'message': 'Leave request approved'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        leave_request = self.get_object()
        leave_request.status = 'rejected'
        leave_request.save()
        return Response({'message': 'Leave request rejected'})


class SalesOrderViewSet(viewsets.ModelViewSet):
    queryset = SalesOrder.objects.all().order_by('-created_at')
    serializer_class = SalesOrderSerializer
    filterset_fields = ['status', 'account']
    search_fields = ['order_number']

    def perform_create(self, serializer):
        order_number = f"SO-{random.randint(100000, 999999)}"
        serializer.save(order_number=order_number)


class SalesOrderLineItemViewSet(viewsets.ModelViewSet):
    queryset = SalesOrderLineItem.objects.all().order_by('-created_at')
    serializer_class = SalesOrderLineItemSerializer
    filterset_fields = ['sales_order', 'product']


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrder.objects.all().order_by('-created_at')
    serializer_class = PurchaseOrderSerializer
    filterset_fields = ['status', 'supplier', 'warehouse']
    search_fields = ['order_number']

    def perform_create(self, serializer):
        order_number = f"PO-{random.randint(100000, 999999)}"
        serializer.save(order_number=order_number)


class PurchaseOrderLineItemViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrderLineItem.objects.all().order_by('-created_at')
    serializer_class = PurchaseOrderLineItemSerializer
    filterset_fields = ['purchase_order', 'product']
