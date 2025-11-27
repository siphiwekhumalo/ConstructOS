from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    WarehouseViewSet, ProductViewSet, StockItemViewSet, InvoiceViewSet,
    InvoiceLineItemViewSet, PaymentViewSet, GeneralLedgerEntryViewSet,
    EmployeeViewSet, PayrollRecordViewSet, LeaveRequestViewSet,
    SalesOrderViewSet, SalesOrderLineItemViewSet,
    PurchaseOrderViewSet, PurchaseOrderLineItemViewSet
)

router = DefaultRouter()
router.register(r'warehouses', WarehouseViewSet)
router.register(r'products', ProductViewSet)
router.register(r'stock', StockItemViewSet)
router.register(r'invoices', InvoiceViewSet)
router.register(r'invoice-line-items', InvoiceLineItemViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'ledger-entries', GeneralLedgerEntryViewSet)
router.register(r'employees', EmployeeViewSet)
router.register(r'payroll', PayrollRecordViewSet)
router.register(r'leave-requests', LeaveRequestViewSet)
router.register(r'sales-orders', SalesOrderViewSet)
router.register(r'sales-order-line-items', SalesOrderLineItemViewSet)
router.register(r'purchase-orders', PurchaseOrderViewSet)
router.register(r'purchase-order-line-items', PurchaseOrderLineItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
