"""
Cash Flow Forecasting API endpoints.
"""
from fastapi import APIRouter, Request, HTTPException
from datetime import datetime, date
from typing import Optional
import httpx

from ..schemas.predictions import CashFlowRequest, CashFlowResponse, CashFlowForecastItem, ModelInfo
from ..config import get_settings

router = APIRouter()
settings = get_settings()


async def fetch_pending_invoices() -> list:
    """Fetch pending invoices from Finance service."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.FINANCE_SERVICE_URL}/api/v1/invoices/?status=pending",
                timeout=10.0
            )
            if response.status_code == 200:
                data = response.json()
                invoices = data.get('results', [])
                return [
                    {
                        'amount': float(inv.get('total_amount', 0) or 0),
                        'due_date': inv.get('due_date'),
                        'probability': 0.7 if inv.get('days_overdue', 0) > 0 else 0.85,
                    }
                    for inv in invoices
                ]
    except Exception:
        pass
    return []


async def fetch_upcoming_payroll() -> list:
    """Fetch upcoming payroll from HR service."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.HR_SERVICE_URL}/api/v1/payroll/upcoming/",
                timeout=10.0
            )
            if response.status_code == 200:
                data = response.json()
                return [
                    {
                        'amount': float(p.get('total_amount', 0) or 0),
                        'date': p.get('payment_date'),
                    }
                    for p in data.get('results', [])
                ]
    except Exception:
        pass
    return []


async def fetch_historical_cashflow() -> dict:
    """Fetch historical cash flow data from Finance service."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.FINANCE_SERVICE_URL}/api/v1/transactions/summary/",
                timeout=10.0
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    'avg_daily_inflow': data.get('avg_daily_inflow', 50000),
                    'avg_daily_outflow': data.get('avg_daily_outflow', 35000),
                    'volatility': data.get('volatility', 0.15),
                }
    except Exception:
        pass
    return {'avg_daily_inflow': 50000, 'avg_daily_outflow': 35000, 'volatility': 0.15}


@router.post("/cashflow/forecast", response_model=CashFlowResponse)
async def forecast_cashflow(
    request: Request,
    forecast_days: int = 30,
    include_pending_invoices: bool = True,
    include_upcoming_payroll: bool = True,
):
    """
    Forecast cash flow for the specified period.
    
    Returns daily predicted inflows, outflows, and net cash flow
    with confidence intervals.
    """
    model_manager = getattr(request.app.state, 'model_manager', None)
    if not model_manager:
        raise HTTPException(status_code=503, detail="Models not loaded")
    
    model = model_manager.get_model('cashflow')
    if not model:
        raise HTTPException(status_code=503, detail="Cash flow model not available")
    
    historical = await fetch_historical_cashflow()
    pending_invoices = await fetch_pending_invoices() if include_pending_invoices else []
    upcoming_payroll = await fetch_upcoming_payroll() if include_upcoming_payroll else []
    
    features = {
        'forecast_days': min(max(forecast_days, 7), 365),
        'avg_daily_inflow': historical['avg_daily_inflow'],
        'avg_daily_outflow': historical['avg_daily_outflow'],
        'volatility': historical['volatility'],
        'pending_invoices': pending_invoices,
        'upcoming_payroll': upcoming_payroll,
    }
    
    prediction = model.predict(features)
    
    forecast_items = [
        CashFlowForecastItem(
            date=date.fromisoformat(item['date']),
            predicted_inflow=item['predicted_inflow'],
            predicted_outflow=item['predicted_outflow'],
            net_cash_flow=item['net_cash_flow'],
            confidence_lower=item['confidence_lower'],
            confidence_upper=item['confidence_upper'],
        )
        for item in prediction['forecast']
    ]
    
    return CashFlowResponse(
        forecast=forecast_items,
        summary=prediction['summary'],
        model_info=ModelInfo(**model.model_info),
        predicted_at=datetime.utcnow(),
    )


@router.get("/cashflow/summary")
async def cashflow_summary(request: Request, days: int = 30):
    """Get a quick cash flow summary without full forecast."""
    response = await forecast_cashflow(request, forecast_days=days)
    return {
        "period_days": days,
        "summary": response.summary,
        "model_info": response.model_info,
    }
