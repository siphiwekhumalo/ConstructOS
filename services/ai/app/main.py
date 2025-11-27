"""
AI Service - FastAPI Application

Provides ML-powered predictions for:
- Credit Risk Scoring
- Cash Flow Forecasting
- Lead Scoring
- Project Delay Prediction
- Predictive Maintenance
- Demand Forecasting
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import get_settings
from .routers import (
    credit_risk,
    cashflow,
    lead_scoring,
    project_delay,
    maintenance,
    demand_forecast,
    health,
)
from .services.model_manager import ModelManager

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager."""
    model_manager = ModelManager()
    await model_manager.load_all_models()
    app.state.model_manager = model_manager
    yield
    await model_manager.cleanup()


app = FastAPI(
    title="ConstructOS AI Service",
    description="Machine Learning predictions for construction management",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["Health"])
app.include_router(credit_risk.router, prefix="/api/v1/ai", tags=["Credit Risk"])
app.include_router(cashflow.router, prefix="/api/v1/ai", tags=["Cash Flow"])
app.include_router(lead_scoring.router, prefix="/api/v1/ai", tags=["Lead Scoring"])
app.include_router(project_delay.router, prefix="/api/v1/ai", tags=["Project Delay"])
app.include_router(maintenance.router, prefix="/api/v1/ai", tags=["Predictive Maintenance"])
app.include_router(demand_forecast.router, prefix="/api/v1/ai", tags=["Demand Forecast"])


@app.get("/")
async def root():
    return {
        "service": "ConstructOS AI Service",
        "version": "1.0.0",
        "endpoints": {
            "credit_risk": "/api/v1/ai/credit-risk/predict/{customer_id}",
            "cashflow": "/api/v1/ai/cashflow/forecast",
            "lead_scoring": "/api/v1/ai/leads/score/{lead_id}",
            "project_delay": "/api/v1/ai/projects/delay-risk/{project_id}",
            "maintenance": "/api/v1/ai/equipment/maintenance-risk/{equipment_id}",
            "demand_forecast": "/api/v1/ai/inventory/demand-forecast/{product_id}",
        }
    }
