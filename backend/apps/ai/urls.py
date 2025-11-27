"""
AI Module URL Configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AIHealthView,
    CreditRiskView,
    LeadScoreView,
    ProjectDelayView,
    MaintenanceRiskView,
    DemandForecastView,
    CashFlowForecastView,
    PredictionLogViewSet,
    ModelMetadataViewSet,
)

router = DefaultRouter()
router.register(r'prediction-logs', PredictionLogViewSet)
router.register(r'models', ModelMetadataViewSet)

urlpatterns = [
    path('health/', AIHealthView.as_view(), name='ai-health'),
    
    path('credit-risk/predict/<uuid:customer_id>/', CreditRiskView.as_view(), name='credit-risk-predict'),
    
    path('leads/score/<uuid:lead_id>/', LeadScoreView.as_view(), name='lead-score'),
    
    path('projects/delay-risk/<uuid:project_id>/', ProjectDelayView.as_view(), name='project-delay'),
    
    path('equipment/maintenance-risk/<uuid:equipment_id>/', MaintenanceRiskView.as_view(), name='maintenance-risk'),
    
    path('inventory/demand-forecast/<uuid:product_id>/', DemandForecastView.as_view(), name='demand-forecast'),
    
    path('cashflow/forecast/', CashFlowForecastView.as_view(), name='cashflow-forecast'),
    
    path('', include(router.urls)),
]
