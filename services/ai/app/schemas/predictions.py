"""
Pydantic schemas for AI prediction requests and responses.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from enum import Enum


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ModelInfo(BaseModel):
    """Information about the ML model used."""
    model_name: str
    model_version: str
    trained_at: Optional[datetime] = None
    accuracy: Optional[float] = None


class CreditRiskRequest(BaseModel):
    """Request for credit risk prediction."""
    customer_id: str
    include_history: bool = True


class CreditRiskResponse(BaseModel):
    """Response for credit risk prediction."""
    customer_id: str
    customer_name: Optional[str] = None
    risk_score: float = Field(..., ge=0, le=100, description="Risk score from 0-100")
    risk_level: RiskLevel
    confidence: float = Field(..., ge=0, le=1)
    factors: List[str] = Field(default_factory=list)
    recommended_credit_limit: Optional[float] = None
    recommended_payment_terms: Optional[str] = None
    model_info: ModelInfo
    predicted_at: datetime = Field(default_factory=datetime.utcnow)


class CashFlowForecastItem(BaseModel):
    """Single item in cash flow forecast."""
    date: date
    predicted_inflow: float
    predicted_outflow: float
    net_cash_flow: float
    confidence_lower: float
    confidence_upper: float


class CashFlowRequest(BaseModel):
    """Request for cash flow forecasting."""
    forecast_days: int = Field(default=30, ge=7, le=365)
    include_pending_invoices: bool = True
    include_upcoming_payroll: bool = True


class CashFlowResponse(BaseModel):
    """Response for cash flow forecasting."""
    forecast: List[CashFlowForecastItem]
    summary: dict
    model_info: ModelInfo
    predicted_at: datetime = Field(default_factory=datetime.utcnow)


class LeadScoreRequest(BaseModel):
    """Request for lead scoring."""
    lead_id: str
    recalculate: bool = False


class LeadScoreResponse(BaseModel):
    """Response for lead scoring."""
    lead_id: str
    lead_name: Optional[str] = None
    score: int = Field(..., ge=0, le=99, description="Lead score from 0-99")
    conversion_probability: float = Field(..., ge=0, le=1)
    priority: str
    factors: List[dict] = Field(default_factory=list)
    recommended_actions: List[str] = Field(default_factory=list)
    model_info: ModelInfo
    predicted_at: datetime = Field(default_factory=datetime.utcnow)


class ProjectDelayRequest(BaseModel):
    """Request for project delay prediction."""
    project_id: str
    milestone_id: Optional[str] = None


class ProjectDelayResponse(BaseModel):
    """Response for project delay prediction."""
    project_id: str
    project_name: Optional[str] = None
    delay_probability: float = Field(..., ge=0, le=1)
    expected_delay_days: int
    risk_level: RiskLevel
    risk_factors: List[dict] = Field(default_factory=list)
    mitigation_suggestions: List[str] = Field(default_factory=list)
    model_info: ModelInfo
    predicted_at: datetime = Field(default_factory=datetime.utcnow)


class MaintenanceRiskRequest(BaseModel):
    """Request for predictive maintenance."""
    equipment_id: str
    days_ahead: int = Field(default=30, ge=1, le=180)


class MaintenanceRiskResponse(BaseModel):
    """Response for predictive maintenance."""
    equipment_id: str
    equipment_name: Optional[str] = None
    failure_probability: float = Field(..., ge=0, le=1)
    risk_level: RiskLevel
    estimated_remaining_life_days: Optional[int] = None
    recommended_maintenance_date: Optional[date] = None
    maintenance_type: Optional[str] = None
    estimated_downtime_hours: Optional[float] = None
    parts_needed: List[str] = Field(default_factory=list)
    model_info: ModelInfo
    predicted_at: datetime = Field(default_factory=datetime.utcnow)


class DemandForecastItem(BaseModel):
    """Single item in demand forecast."""
    date: date
    predicted_demand: float
    confidence_lower: float
    confidence_upper: float


class DemandForecastRequest(BaseModel):
    """Request for demand forecasting."""
    product_id: str
    warehouse_id: Optional[str] = None
    forecast_days: int = Field(default=30, ge=7, le=180)


class DemandForecastResponse(BaseModel):
    """Response for demand forecasting."""
    product_id: str
    product_name: Optional[str] = None
    warehouse_id: Optional[str] = None
    forecast: List[DemandForecastItem]
    current_stock: Optional[float] = None
    reorder_point: Optional[float] = None
    suggested_order_quantity: Optional[float] = None
    stockout_risk_date: Optional[date] = None
    model_info: ModelInfo
    predicted_at: datetime = Field(default_factory=datetime.utcnow)
