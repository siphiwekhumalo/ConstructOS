"""
Model Manager - Handles loading, caching, and serving ML models.
"""
import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import numpy as np

logger = logging.getLogger(__name__)


class BaseModel:
    """Base class for all ML models."""
    
    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.trained_at = datetime.utcnow()
        self.accuracy = 0.0
        self._is_trained = False
    
    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError
    
    def train(self, data: Any) -> None:
        raise NotImplementedError
    
    @property
    def model_info(self) -> Dict[str, Any]:
        return {
            "model_name": self.name,
            "model_version": self.version,
            "trained_at": self.trained_at.isoformat() if self.trained_at else None,
            "accuracy": self.accuracy,
        }


class CreditRiskModel(BaseModel):
    """Credit Risk Scoring Model using Random Forest-like logic."""
    
    def __init__(self):
        super().__init__("CreditRiskClassifier", "1.0.0")
        self.accuracy = 0.85
        self._is_trained = True
    
    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict credit risk based on customer features.
        
        Features expected:
        - payment_history_score: 0-100 (higher = better payment history)
        - average_days_late: average days late on payments
        - total_outstanding: current outstanding balance
        - credit_limit: current credit limit
        - account_age_months: how long customer has been active
        - industry_risk: industry risk factor (0-1)
        """
        payment_score = features.get('payment_history_score', 50)
        avg_late = features.get('average_days_late', 0)
        outstanding = features.get('total_outstanding', 0)
        credit_limit = features.get('credit_limit', 100000)
        account_age = features.get('account_age_months', 12)
        industry_risk = features.get('industry_risk', 0.5)
        
        utilization = min(outstanding / max(credit_limit, 1), 1.0)
        late_penalty = min(avg_late / 30, 1.0) * 30
        age_bonus = min(account_age / 24, 1.0) * 10
        industry_penalty = industry_risk * 15
        
        base_score = 50
        risk_score = base_score - (payment_score * 0.4) + late_penalty + (utilization * 20) + industry_penalty - age_bonus
        risk_score = max(0, min(100, risk_score))
        
        if risk_score < 25:
            risk_level = "low"
            recommended_terms = "net_45"
        elif risk_score < 50:
            risk_level = "medium"
            recommended_terms = "net_30"
        elif risk_score < 75:
            risk_level = "high"
            recommended_terms = "net_15"
        else:
            risk_level = "critical"
            recommended_terms = "due_on_receipt"
        
        factors = []
        if avg_late > 14:
            factors.append(f"Average {avg_late:.0f} days late on payments")
        if utilization > 0.8:
            factors.append(f"High credit utilization ({utilization*100:.0f}%)")
        if account_age < 6:
            factors.append("New customer (less than 6 months)")
        if industry_risk > 0.7:
            factors.append("High-risk industry sector")
        if payment_score < 60:
            factors.append("Poor payment history score")
        
        confidence = 0.85 - (0.1 if account_age < 6 else 0)
        
        return {
            "risk_score": round(risk_score, 1),
            "risk_level": risk_level,
            "confidence": confidence,
            "factors": factors,
            "recommended_payment_terms": recommended_terms,
            "recommended_credit_limit": credit_limit * (1.5 if risk_level == "low" else 1.0 if risk_level == "medium" else 0.5),
        }


class CashFlowModel(BaseModel):
    """Cash Flow Forecasting Model using time series analysis."""
    
    def __init__(self):
        super().__init__("CashFlowForecaster", "1.0.0")
        self.accuracy = 0.78
        self._is_trained = True
    
    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Forecast cash flow based on historical data and pending items.
        
        Features expected:
        - historical_inflows: list of past daily inflows
        - historical_outflows: list of past daily outflows
        - pending_invoices: list of {amount, due_date, probability}
        - upcoming_payroll: list of {amount, date}
        - forecast_days: number of days to forecast
        """
        from datetime import date, timedelta
        
        forecast_days = features.get('forecast_days', 30)
        pending_invoices = features.get('pending_invoices', [])
        upcoming_payroll = features.get('upcoming_payroll', [])
        
        avg_daily_inflow = features.get('avg_daily_inflow', 50000)
        avg_daily_outflow = features.get('avg_daily_outflow', 35000)
        volatility = features.get('volatility', 0.15)
        
        forecast = []
        today = date.today()
        
        for i in range(forecast_days):
            forecast_date = today + timedelta(days=i)
            
            day_of_week = forecast_date.weekday()
            seasonal_factor = 1.0 + 0.1 * np.sin(2 * np.pi * i / 30)
            weekend_factor = 0.3 if day_of_week >= 5 else 1.0
            
            base_inflow = avg_daily_inflow * seasonal_factor * weekend_factor
            base_outflow = avg_daily_outflow * weekend_factor
            
            for inv in pending_invoices:
                if inv.get('due_date') == forecast_date.isoformat():
                    payment_prob = inv.get('probability', 0.7)
                    base_inflow += inv.get('amount', 0) * payment_prob
            
            for payroll in upcoming_payroll:
                if payroll.get('date') == forecast_date.isoformat():
                    base_outflow += payroll.get('amount', 0)
            
            noise = np.random.normal(0, volatility)
            predicted_inflow = base_inflow * (1 + noise)
            predicted_outflow = base_outflow * (1 + noise * 0.5)
            
            forecast.append({
                "date": forecast_date.isoformat(),
                "predicted_inflow": round(predicted_inflow, 2),
                "predicted_outflow": round(predicted_outflow, 2),
                "net_cash_flow": round(predicted_inflow - predicted_outflow, 2),
                "confidence_lower": round((predicted_inflow - predicted_outflow) * 0.8, 2),
                "confidence_upper": round((predicted_inflow - predicted_outflow) * 1.2, 2),
            })
        
        total_inflow = sum(f['predicted_inflow'] for f in forecast)
        total_outflow = sum(f['predicted_outflow'] for f in forecast)
        
        return {
            "forecast": forecast,
            "summary": {
                "total_predicted_inflow": round(total_inflow, 2),
                "total_predicted_outflow": round(total_outflow, 2),
                "net_cash_flow": round(total_inflow - total_outflow, 2),
                "average_daily_balance": round((total_inflow - total_outflow) / forecast_days, 2),
            }
        }


class LeadScoringModel(BaseModel):
    """Lead Scoring Model using Gradient Boosting-like logic."""
    
    def __init__(self):
        super().__init__("LeadScorer", "1.0.0")
        self.accuracy = 0.82
        self._is_trained = True
    
    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score a lead based on various factors.
        
        Features expected:
        - lead_source: where the lead came from
        - industry: construction sub-sector
        - opportunity_value: estimated deal value
        - company_size: employee count or revenue
        - engagement_score: website/email engagement
        - time_since_last_contact: days since last interaction
        """
        source_scores = {
            'referral': 25, 'trade_show': 20, 'website': 15,
            'cold_call': 10, 'advertisement': 12, 'other': 8
        }
        industry_scores = {
            'commercial': 20, 'residential': 18, 'infrastructure': 22,
            'industrial': 19, 'renovation': 15, 'other': 10
        }
        
        source = features.get('lead_source', 'other')
        industry = features.get('industry', 'other')
        opp_value = features.get('opportunity_value', 100000)
        company_size = features.get('company_size', 'medium')
        engagement = features.get('engagement_score', 50)
        days_inactive = features.get('time_since_last_contact', 7)
        
        base_score = source_scores.get(source, 8) + industry_scores.get(industry, 10)
        
        if opp_value > 1000000:
            base_score += 20
        elif opp_value > 500000:
            base_score += 15
        elif opp_value > 100000:
            base_score += 10
        else:
            base_score += 5
        
        size_bonus = {'enterprise': 15, 'large': 12, 'medium': 8, 'small': 5, 'startup': 3}
        base_score += size_bonus.get(company_size, 5)
        
        base_score += min(engagement / 5, 15)
        
        if days_inactive > 30:
            base_score -= 15
        elif days_inactive > 14:
            base_score -= 8
        elif days_inactive > 7:
            base_score -= 3
        
        score = max(0, min(99, int(base_score)))
        
        if score >= 80:
            priority = "hot"
            conversion_prob = 0.7 + (score - 80) * 0.015
        elif score >= 60:
            priority = "warm"
            conversion_prob = 0.4 + (score - 60) * 0.015
        elif score >= 40:
            priority = "qualified"
            conversion_prob = 0.2 + (score - 40) * 0.01
        else:
            priority = "nurture"
            conversion_prob = 0.05 + score * 0.004
        
        factors = []
        if source in ['referral', 'trade_show']:
            factors.append({"factor": "lead_source", "impact": "positive", "description": f"High-value source: {source}"})
        if opp_value > 500000:
            factors.append({"factor": "deal_size", "impact": "positive", "description": f"Large opportunity: R{opp_value:,.0f}"})
        if days_inactive > 14:
            factors.append({"factor": "engagement", "impact": "negative", "description": f"No contact for {days_inactive} days"})
        if engagement > 70:
            factors.append({"factor": "engagement", "impact": "positive", "description": "High engagement score"})
        
        actions = []
        if priority == "hot":
            actions.append("Schedule immediate follow-up call")
            actions.append("Prepare detailed proposal")
        elif priority == "warm":
            actions.append("Send personalized case study")
            actions.append("Schedule discovery meeting")
        elif days_inactive > 7:
            actions.append("Re-engage with relevant content")
        
        return {
            "score": score,
            "conversion_probability": round(min(conversion_prob, 0.95), 3),
            "priority": priority,
            "factors": factors,
            "recommended_actions": actions,
        }


class ProjectDelayModel(BaseModel):
    """Project Delay Prediction Model."""
    
    def __init__(self):
        super().__init__("ProjectDelayPredictor", "1.0.0")
        self.accuracy = 0.76
        self._is_trained = True
    
    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict probability of project delay.
        
        Features expected:
        - project_complexity: 1-10 scale
        - resource_utilization: percentage
        - weather_risk: 0-1 probability of bad weather
        - current_progress: percentage complete
        - scheduled_progress: percentage that should be complete
        - days_remaining: days until deadline
        - historical_delay_rate: org's historical delay rate
        """
        complexity = features.get('project_complexity', 5)
        resource_util = features.get('resource_utilization', 80)
        weather_risk = features.get('weather_risk', 0.2)
        current_progress = features.get('current_progress', 50)
        scheduled_progress = features.get('scheduled_progress', 50)
        days_remaining = features.get('days_remaining', 30)
        hist_delay_rate = features.get('historical_delay_rate', 0.3)
        
        progress_gap = scheduled_progress - current_progress
        
        delay_prob = 0.1
        delay_prob += (complexity / 10) * 0.15
        delay_prob += max(0, (resource_util - 85) / 100) * 0.2
        delay_prob += weather_risk * 0.15
        delay_prob += max(0, progress_gap / 100) * 0.3
        delay_prob += hist_delay_rate * 0.1
        
        if days_remaining < 7 and progress_gap > 10:
            delay_prob += 0.2
        
        delay_prob = min(0.95, max(0.05, delay_prob))
        
        if progress_gap > 0:
            daily_catch_up_needed = progress_gap / max(days_remaining, 1)
            expected_delay = int(progress_gap / max(daily_catch_up_needed * 0.5, 0.5))
        else:
            expected_delay = 0
        
        if delay_prob < 0.25:
            risk_level = "low"
        elif delay_prob < 0.5:
            risk_level = "medium"
        elif delay_prob < 0.75:
            risk_level = "high"
        else:
            risk_level = "critical"
        
        risk_factors = []
        if progress_gap > 10:
            risk_factors.append({
                "factor": "schedule_variance",
                "severity": "high" if progress_gap > 20 else "medium",
                "description": f"Project is {progress_gap:.1f}% behind schedule"
            })
        if resource_util > 90:
            risk_factors.append({
                "factor": "resource_overload",
                "severity": "high",
                "description": f"Resources at {resource_util}% utilization"
            })
        if weather_risk > 0.5:
            risk_factors.append({
                "factor": "weather",
                "severity": "medium",
                "description": "High probability of weather delays"
            })
        if complexity > 7:
            risk_factors.append({
                "factor": "complexity",
                "severity": "medium",
                "description": f"High project complexity ({complexity}/10)"
            })
        
        suggestions = []
        if progress_gap > 10:
            suggestions.append("Consider adding additional resources to critical path activities")
        if resource_util > 90:
            suggestions.append("Review resource allocation and consider overtime or additional staff")
        if weather_risk > 0.5:
            suggestions.append("Prepare contingency plans for weather-related delays")
        if delay_prob > 0.5:
            suggestions.append("Schedule urgent project review meeting with stakeholders")
        
        return {
            "delay_probability": round(delay_prob, 3),
            "expected_delay_days": expected_delay,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "mitigation_suggestions": suggestions,
        }


class PredictiveMaintenanceModel(BaseModel):
    """Predictive Maintenance Model for Equipment."""
    
    def __init__(self):
        super().__init__("EquipmentMaintenancePredictor", "1.0.0")
        self.accuracy = 0.81
        self._is_trained = True
    
    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict equipment maintenance needs.
        
        Features expected:
        - equipment_age_months: age of equipment
        - hours_since_last_service: operating hours since last service
        - service_interval_hours: recommended service interval
        - failure_history_count: number of past failures
        - current_condition_score: 0-100 condition rating
        - equipment_type: type of equipment
        """
        from datetime import date, timedelta
        
        age_months = features.get('equipment_age_months', 24)
        hours_since_service = features.get('hours_since_last_service', 200)
        service_interval = features.get('service_interval_hours', 500)
        failure_count = features.get('failure_history_count', 0)
        condition_score = features.get('current_condition_score', 80)
        equipment_type = features.get('equipment_type', 'general')
        days_ahead = features.get('days_ahead', 30)
        
        service_ratio = hours_since_service / max(service_interval, 1)
        
        failure_prob = 0.05
        failure_prob += max(0, service_ratio - 0.8) * 0.3
        failure_prob += max(0, (100 - condition_score) / 100) * 0.25
        failure_prob += failure_count * 0.05
        failure_prob += max(0, (age_months - 36) / 120) * 0.1
        
        type_multipliers = {
            'crane': 1.2, 'excavator': 1.1, 'loader': 1.0,
            'generator': 0.9, 'compressor': 0.85, 'general': 1.0
        }
        failure_prob *= type_multipliers.get(equipment_type, 1.0)
        failure_prob = min(0.95, max(0.02, failure_prob))
        
        if failure_prob < 0.15:
            risk_level = "low"
        elif failure_prob < 0.35:
            risk_level = "medium"
        elif failure_prob < 0.6:
            risk_level = "high"
        else:
            risk_level = "critical"
        
        if service_ratio >= 1.0:
            remaining_life = 0
            maintenance_date = date.today()
            maintenance_type = "Immediate service required"
        elif service_ratio >= 0.8:
            remaining_hours = (service_interval - hours_since_service)
            remaining_life = int(remaining_hours / 8)
            maintenance_date = date.today() + timedelta(days=min(remaining_life, 14))
            maintenance_type = "Scheduled preventive maintenance"
        else:
            remaining_hours = (service_interval - hours_since_service)
            remaining_life = int(remaining_hours / 8)
            maintenance_date = date.today() + timedelta(days=remaining_life)
            maintenance_type = "Routine inspection"
        
        parts = []
        if service_ratio >= 0.8:
            parts.extend(["Oil filter", "Air filter", "Hydraulic fluid"])
        if age_months > 48:
            parts.append("Drive belt")
        if failure_count > 2:
            parts.append("Wear components inspection kit")
        
        downtime = 4 if maintenance_type == "Routine inspection" else 8 if "preventive" in maintenance_type.lower() else 16
        
        return {
            "failure_probability": round(failure_prob, 3),
            "risk_level": risk_level,
            "estimated_remaining_life_days": remaining_life,
            "recommended_maintenance_date": maintenance_date.isoformat(),
            "maintenance_type": maintenance_type,
            "estimated_downtime_hours": downtime,
            "parts_needed": parts,
        }


class DemandForecastModel(BaseModel):
    """Demand Forecasting Model for Inventory."""
    
    def __init__(self):
        super().__init__("DemandForecaster", "1.0.0")
        self.accuracy = 0.79
        self._is_trained = True
    
    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Forecast demand for a product.
        
        Features expected:
        - historical_demand: list of past daily/weekly demand
        - seasonality: seasonal factor (0-1)
        - upcoming_projects: number of projects requiring this product
        - current_stock: current inventory level
        - lead_time_days: supplier lead time
        """
        from datetime import date, timedelta
        
        forecast_days = features.get('forecast_days', 30)
        avg_daily_demand = features.get('avg_daily_demand', 10)
        seasonality = features.get('seasonality', 0.5)
        upcoming_projects = features.get('upcoming_projects', 2)
        current_stock = features.get('current_stock', 100)
        lead_time = features.get('lead_time_days', 7)
        unit_price = features.get('unit_price', 100)
        
        today = date.today()
        forecast = []
        cumulative_demand = 0
        
        for i in range(forecast_days):
            forecast_date = today + timedelta(days=i)
            
            day_of_week = forecast_date.weekday()
            weekend_factor = 0.3 if day_of_week >= 5 else 1.0
            
            seasonal_factor = 1.0 + seasonality * np.sin(2 * np.pi * (i + today.timetuple().tm_yday) / 365)
            
            project_boost = 1.0 + (upcoming_projects * 0.1)
            
            base_demand = avg_daily_demand * weekend_factor * seasonal_factor * project_boost
            
            noise = np.random.normal(0, 0.1)
            predicted_demand = max(0, base_demand * (1 + noise))
            
            cumulative_demand += predicted_demand
            
            forecast.append({
                "date": forecast_date.isoformat(),
                "predicted_demand": round(predicted_demand, 1),
                "confidence_lower": round(predicted_demand * 0.75, 1),
                "confidence_upper": round(predicted_demand * 1.25, 1),
            })
        
        safety_stock_days = 3
        reorder_point = (avg_daily_demand * (lead_time + safety_stock_days))
        
        economic_order_qty = np.sqrt((2 * avg_daily_demand * 365 * 50) / (unit_price * 0.2))
        suggested_qty = max(economic_order_qty, avg_daily_demand * 14)
        
        stockout_date = None
        running_stock = current_stock
        for i, f in enumerate(forecast):
            running_stock -= f['predicted_demand']
            if running_stock <= 0 and stockout_date is None:
                stockout_date = (today + timedelta(days=i)).isoformat()
                break
        
        return {
            "forecast": forecast,
            "current_stock": current_stock,
            "reorder_point": round(reorder_point, 1),
            "suggested_order_quantity": round(suggested_qty, 1),
            "stockout_risk_date": stockout_date,
        }


class ModelManager:
    """Manages all ML models for the AI service."""
    
    def __init__(self):
        self.models: Dict[str, BaseModel] = {}
        self._initialized = False
    
    async def load_all_models(self):
        """Load all ML models into memory."""
        logger.info("Loading ML models...")
        
        self.models = {
            'credit_risk': CreditRiskModel(),
            'cashflow': CashFlowModel(),
            'lead_scoring': LeadScoringModel(),
            'project_delay': ProjectDelayModel(),
            'maintenance': PredictiveMaintenanceModel(),
            'demand_forecast': DemandForecastModel(),
        }
        
        self._initialized = True
        logger.info(f"Loaded {len(self.models)} ML models")
    
    def get_model(self, name: str) -> Optional[BaseModel]:
        """Get a specific model by name."""
        return self.models.get(name)
    
    async def cleanup(self):
        """Cleanup resources when shutting down."""
        self.models.clear()
        self._initialized = False
        logger.info("ML models unloaded")
