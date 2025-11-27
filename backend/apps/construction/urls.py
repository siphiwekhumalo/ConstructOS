from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProjectViewSet, TransactionViewSet, EquipmentViewSet,
    SafetyInspectionViewSet, DocumentViewSet, DashboardView, PowerBIConfigView
)

router = DefaultRouter()
router.register(r'projects', ProjectViewSet)
router.register(r'transactions', TransactionViewSet)
router.register(r'equipment', EquipmentViewSet)
router.register(r'safety/inspections', SafetyInspectionViewSet, basename='safety-inspections')
router.register(r'documents', DocumentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('analytics/dashboard/', DashboardView.as_view(), name='dashboard'),
    path('powerbi/config/', PowerBIConfigView.as_view(), name='powerbi-config'),
]
