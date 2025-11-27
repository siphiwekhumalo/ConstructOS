"""
AI Module API Views.

Provides endpoints for:
- Credit Risk Scoring
- Cash Flow Forecasting
- Lead Scoring
- Project Delay Prediction
- Predictive Maintenance
- Demand Forecasting
"""
import time
from datetime import datetime
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.db.models import Avg, Sum, F

from .models import PredictionLog, ModelMetadata, FeatureStore
from .serializers import PredictionLogSerializer, ModelMetadataSerializer
from .ml_models import ModelRegistry


def log_prediction(prediction_type, entity_type, entity_id, features, result, model, user=None, processing_time=None):
    """Log a prediction for auditing."""
    try:
        PredictionLog.objects.create(
            prediction_type=prediction_type,
            entity_type=entity_type,
            entity_id=str(entity_id),
            input_features=features,
            prediction_result=result,
            model_name=model.name,
            model_version=model.version,
            confidence=result.get('confidence'),
            requested_by=user if user and hasattr(user, 'id') else None,
            processing_time_ms=processing_time,
        )
    except Exception:
        pass


class AIHealthView(APIView):
    """Health check for AI module."""
    permission_classes = [AllowAny]
    
    def get(self, request):
        registry = ModelRegistry()
        return Response({
            'status': 'healthy',
            'models': registry.get_all_model_info(),
        })


class CreditRiskView(APIView):
    """Credit risk scoring endpoint."""
    permission_classes = [AllowAny]
    
    def get(self, request, customer_id):
        start_time = time.time()
        registry = ModelRegistry()
        model = registry.get_model('credit_risk')
        
        if not model:
            return Response({'error': 'Model not available'}, status=503)
        
        customer_name = None
        credit_limit = 100000
        industry = 'construction'
        account_age = 12
        payment_score = 50
        avg_late = 0
        outstanding = 0
        
        try:
            from backend.apps.crm.models import Account
            account = Account.objects.get(id=customer_id)
            customer_name = account.name
            credit_limit = float(account.credit_limit or 100000)
            industry = account.industry or 'construction'
            if account.created_at:
                account_age = (datetime.now(account.created_at.tzinfo) - account.created_at).days / 30
        except Exception:
            pass
        
        try:
            from backend.apps.erp.models import Invoice, Payment
            payments = Payment.objects.filter(invoice__account_id=customer_id)
            if payments.exists():
                total_late_days = 0
                on_time_count = 0
                for p in payments:
                    if p.payment_date and hasattr(p, 'invoice') and p.invoice.due_date:
                        days_late = (p.payment_date - p.invoice.due_date).days
                        total_late_days += max(0, days_late)
                        if days_late <= 0:
                            on_time_count += 1
                avg_late = total_late_days / payments.count()
                payment_score = (on_time_count / payments.count()) * 100
            
            outstanding = Invoice.objects.filter(
                account_id=customer_id, 
                status__in=['pending', 'overdue']
            ).aggregate(total=Sum('total_amount'))['total'] or 0
        except Exception:
            pass
        
        industry_risk_map = {
            'construction': 0.5, 'residential': 0.4, 'commercial': 0.45,
            'infrastructure': 0.55, 'mining': 0.6,
        }
        industry_risk = industry_risk_map.get(industry.lower() if industry else '', 0.5)
        
        features = {
            'payment_history_score': payment_score,
            'average_days_late': avg_late,
            'total_outstanding': float(outstanding),
            'credit_limit': credit_limit,
            'account_age_months': account_age,
            'industry_risk': industry_risk,
        }
        
        result = model.predict(features)
        processing_time = int((time.time() - start_time) * 1000)
        
        log_prediction(
            'credit_risk', 'account', customer_id,
            features, result, model, request.user, processing_time
        )
        
        return Response({
            'customer_id': str(customer_id),
            'customer_name': customer_name,
            **result,
            'model_info': model.model_info,
            'predicted_at': datetime.utcnow().isoformat(),
        })


class LeadScoreView(APIView):
    """Lead scoring endpoint."""
    permission_classes = [AllowAny]
    
    def get(self, request, lead_id):
        start_time = time.time()
        registry = ModelRegistry()
        model = registry.get_model('lead_scoring')
        
        if not model:
            return Response({'error': 'Model not available'}, status=503)
        
        lead_name = None
        source = 'website'
        industry = 'construction'
        opp_value = 100000
        
        try:
            from backend.apps.crm.models import Lead
            lead = Lead.objects.get(id=lead_id)
            lead_name = lead.company_name or f"{lead.first_name} {lead.last_name}"
            source = lead.source or 'website'
            industry = lead.industry or 'construction'
            opp_value = float(lead.estimated_value or 100000)
        except Exception:
            pass
        
        features = {
            'lead_source': source,
            'industry': industry,
            'opportunity_value': opp_value,
            'company_size': 'medium',
            'engagement_score': 50,
            'time_since_last_contact': 7,
        }
        
        result = model.predict(features)
        processing_time = int((time.time() - start_time) * 1000)
        
        log_prediction(
            'lead_score', 'lead', lead_id,
            features, result, model, request.user, processing_time
        )
        
        return Response({
            'lead_id': str(lead_id),
            'lead_name': lead_name,
            **result,
            'model_info': model.model_info,
            'predicted_at': datetime.utcnow().isoformat(),
        })


class ProjectDelayView(APIView):
    """Project delay prediction endpoint."""
    permission_classes = [AllowAny]
    
    def get(self, request, project_id):
        start_time = time.time()
        registry = ModelRegistry()
        model = registry.get_model('project_delay')
        
        if not model:
            return Response({'error': 'Model not available'}, status=503)
        
        project_name = None
        current_progress = 50
        scheduled_progress = 50
        days_remaining = 30
        
        try:
            from backend.apps.construction.models import Project
            project = Project.objects.get(id=project_id)
            project_name = project.name
            current_progress = float(project.progress or 50)
            
            if project.start_date and project.due_date:
                total_days = (project.due_date - project.start_date).days
                elapsed_days = (datetime.now().date() - project.start_date).days
                days_remaining = max((project.due_date - datetime.now().date()).days, 1)
                scheduled_progress = (elapsed_days / max(total_days, 1)) * 100
        except Exception:
            pass
        
        features = {
            'project_complexity': 6,
            'resource_utilization': 80,
            'weather_risk': 0.2,
            'current_progress': current_progress,
            'scheduled_progress': scheduled_progress,
            'days_remaining': days_remaining,
            'historical_delay_rate': 0.3,
        }
        
        result = model.predict(features)
        processing_time = int((time.time() - start_time) * 1000)
        
        log_prediction(
            'project_delay', 'project', project_id,
            features, result, model, request.user, processing_time
        )
        
        return Response({
            'project_id': str(project_id),
            'project_name': project_name,
            **result,
            'model_info': model.model_info,
            'predicted_at': datetime.utcnow().isoformat(),
        })


class MaintenanceRiskView(APIView):
    """Predictive maintenance endpoint."""
    permission_classes = [AllowAny]
    
    def get(self, request, equipment_id):
        start_time = time.time()
        registry = ModelRegistry()
        model = registry.get_model('maintenance')
        
        if not model:
            return Response({'error': 'Model not available'}, status=503)
        
        equipment_name = None
        age_months = 24
        hours_since_service = 200
        condition_score = 75
        equipment_type = 'general'
        
        try:
            from backend.apps.construction.models import Equipment
            equipment = Equipment.objects.get(id=equipment_id)
            equipment_name = equipment.name
            
            if hasattr(equipment, 'purchase_date') and equipment.purchase_date:
                age_months = (datetime.now().date() - equipment.purchase_date).days / 30
            
            if hasattr(equipment, 'operating_hours'):
                operating_hours = float(equipment.operating_hours or 0)
                last_service_hours = float(getattr(equipment, 'last_service_hours', 0) or 0)
                hours_since_service = operating_hours - last_service_hours
            
            if hasattr(equipment, 'condition_score'):
                condition_score = float(equipment.condition_score or 75)
            
            equipment_type = (getattr(equipment, 'type', None) or getattr(equipment, 'category', None) or 'general').lower()
        except Exception:
            pass
        
        service_intervals = {
            'crane': 250, 'excavator': 300, 'loader': 400,
            'generator': 500, 'compressor': 600, 'general': 500
        }
        
        features = {
            'equipment_age_months': age_months,
            'hours_since_last_service': max(hours_since_service, 0),
            'service_interval_hours': service_intervals.get(equipment_type, 500),
            'failure_history_count': 0,
            'current_condition_score': condition_score,
            'equipment_type': equipment_type,
        }
        
        result = model.predict(features)
        processing_time = int((time.time() - start_time) * 1000)
        
        log_prediction(
            'maintenance', 'equipment', equipment_id,
            features, result, model, request.user, processing_time
        )
        
        return Response({
            'equipment_id': str(equipment_id),
            'equipment_name': equipment_name,
            **result,
            'model_info': model.model_info,
            'predicted_at': datetime.utcnow().isoformat(),
        })


class DemandForecastView(APIView):
    """Demand forecasting endpoint."""
    permission_classes = [AllowAny]
    
    def get(self, request, product_id):
        start_time = time.time()
        registry = ModelRegistry()
        model = registry.get_model('demand_forecast')
        
        if not model:
            return Response({'error': 'Model not available'}, status=503)
        
        warehouse_id = request.query_params.get('warehouse_id')
        forecast_days = int(request.query_params.get('forecast_days', 30))
        
        product_name = None
        unit_price = 100
        lead_time = 7
        current_stock = 0
        
        try:
            from backend.apps.erp.models import Product, Stock
            product = Product.objects.get(id=product_id)
            product_name = product.name
            unit_price = float(product.price or 100)
            lead_time = int(getattr(product, 'lead_time_days', 7) or 7)
            
            stock_query = Stock.objects.filter(product_id=product_id)
            if warehouse_id:
                stock_query = stock_query.filter(warehouse_id=warehouse_id)
            current_stock = stock_query.aggregate(total=Sum('quantity'))['total'] or 0
        except Exception:
            pass
        
        features = {
            'forecast_days': min(max(forecast_days, 7), 180),
            'avg_daily_demand': 10,
            'seasonality': 0.3,
            'upcoming_projects': 2,
            'current_stock': float(current_stock),
            'lead_time_days': lead_time,
            'unit_price': unit_price,
        }
        
        result = model.predict(features)
        processing_time = int((time.time() - start_time) * 1000)
        
        log_prediction(
            'demand', 'product', product_id,
            features, result, model, request.user, processing_time
        )
        
        return Response({
            'product_id': str(product_id),
            'product_name': product_name,
            'warehouse_id': warehouse_id,
            **result,
            'model_info': model.model_info,
            'predicted_at': datetime.utcnow().isoformat(),
        })


class CashFlowForecastView(APIView):
    """Cash flow forecasting endpoint."""
    permission_classes = [AllowAny]
    
    def post(self, request):
        start_time = time.time()
        registry = ModelRegistry()
        model = registry.get_model('cashflow')
        
        if not model:
            return Response({'error': 'Model not available'}, status=503)
        
        forecast_days = request.data.get('forecast_days', 30)
        include_pending = request.data.get('include_pending_invoices', True)
        include_payroll = request.data.get('include_upcoming_payroll', True)
        
        pending_invoices = []
        if include_pending:
            try:
                from backend.apps.erp.models import Invoice
                invoices = Invoice.objects.filter(status__in=['pending', 'sent'])
                pending_invoices = [
                    {
                        'amount': float(inv.total_amount or 0),
                        'due_date': inv.due_date.isoformat() if inv.due_date else None,
                        'probability': 0.7 if getattr(inv, 'days_overdue', 0) > 0 else 0.85,
                    }
                    for inv in invoices
                ]
            except Exception:
                pass
        
        upcoming_payroll = []
        if include_payroll:
            try:
                from backend.apps.erp.models import Payroll
                payrolls = Payroll.objects.filter(status='pending')
                upcoming_payroll = [
                    {
                        'amount': float(p.net_pay or 0),
                        'date': p.payment_date.isoformat() if p.payment_date else None,
                    }
                    for p in payrolls
                ]
            except Exception:
                pass
        
        features = {
            'forecast_days': min(max(forecast_days, 7), 365),
            'avg_daily_inflow': 50000,
            'avg_daily_outflow': 35000,
            'volatility': 0.15,
            'pending_invoices': pending_invoices,
            'upcoming_payroll': upcoming_payroll,
        }
        
        result = model.predict(features)
        processing_time = int((time.time() - start_time) * 1000)
        
        log_prediction(
            'cashflow', 'organization', 'global',
            features, result, model, request.user, processing_time
        )
        
        return Response({
            **result,
            'model_info': model.model_info,
            'predicted_at': datetime.utcnow().isoformat(),
        })


class PredictionLogViewSet(viewsets.ReadOnlyModelViewSet):
    """View prediction logs."""
    queryset = PredictionLog.objects.all()
    serializer_class = PredictionLogSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['prediction_type', 'entity_type']


class ModelMetadataViewSet(viewsets.ReadOnlyModelViewSet):
    """View model metadata."""
    queryset = ModelMetadata.objects.all()
    serializer_class = ModelMetadataSerializer
    permission_classes = [AllowAny]
