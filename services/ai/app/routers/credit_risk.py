"""
Credit Risk Scoring API endpoints.
"""
from fastapi import APIRouter, Request, HTTPException
from datetime import datetime
import httpx

from ..schemas.predictions import CreditRiskRequest, CreditRiskResponse, RiskLevel, ModelInfo
from ..config import get_settings

router = APIRouter()
settings = get_settings()


async def fetch_customer_data(customer_id: str) -> dict:
    """Fetch customer data from Identity service."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.IDENTITY_SERVICE_URL}/api/v1/accounts/{customer_id}/",
                timeout=10.0
            )
            if response.status_code == 200:
                return response.json()
    except Exception:
        pass
    return {}


async def fetch_payment_history(customer_id: str) -> dict:
    """Fetch payment history from Finance service."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.FINANCE_SERVICE_URL}/api/v1/payments/?account_id={customer_id}",
                timeout=10.0
            )
            if response.status_code == 200:
                data = response.json()
                payments = data.get('results', [])
                
                if payments:
                    total_late_days = sum(p.get('days_late', 0) for p in payments)
                    avg_late = total_late_days / len(payments)
                    on_time = sum(1 for p in payments if p.get('days_late', 0) <= 0)
                    payment_score = (on_time / len(payments)) * 100
                else:
                    avg_late = 0
                    payment_score = 50
                
                return {
                    'payment_history_score': payment_score,
                    'average_days_late': avg_late,
                    'payment_count': len(payments),
                }
    except Exception:
        pass
    return {'payment_history_score': 50, 'average_days_late': 0, 'payment_count': 0}


@router.get("/credit-risk/predict/{customer_id}", response_model=CreditRiskResponse)
async def predict_credit_risk(customer_id: str, request: Request, include_history: bool = True):
    """
    Predict credit risk for a customer.
    
    Returns a risk score (0-100) and risk classification (low/medium/high/critical)
    based on payment history, credit utilization, and other factors.
    """
    model_manager = getattr(request.app.state, 'model_manager', None)
    if not model_manager:
        raise HTTPException(status_code=503, detail="Models not loaded")
    
    model = model_manager.get_model('credit_risk')
    if not model:
        raise HTTPException(status_code=503, detail="Credit risk model not available")
    
    customer_data = await fetch_customer_data(customer_id)
    payment_data = await fetch_payment_history(customer_id) if include_history else {}
    
    customer_name = customer_data.get('name')
    credit_limit = float(customer_data.get('credit_limit', 100000) or 100000)
    
    industry_risk_map = {
        'construction': 0.5, 'residential': 0.4, 'commercial': 0.45,
        'infrastructure': 0.55, 'mining': 0.6, 'retail': 0.35,
    }
    industry = customer_data.get('industry', 'construction')
    industry_risk = industry_risk_map.get(industry.lower() if industry else 'construction', 0.5)
    
    from datetime import datetime
    created_at = customer_data.get('created_at')
    if created_at:
        try:
            created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            account_age = (datetime.now(created_date.tzinfo) - created_date).days / 30
        except:
            account_age = 12
    else:
        account_age = 12
    
    features = {
        'payment_history_score': payment_data.get('payment_history_score', 50),
        'average_days_late': payment_data.get('average_days_late', 0),
        'total_outstanding': float(customer_data.get('balance_due', 0) or 0),
        'credit_limit': credit_limit,
        'account_age_months': account_age,
        'industry_risk': industry_risk,
    }
    
    prediction = model.predict(features)
    
    return CreditRiskResponse(
        customer_id=customer_id,
        customer_name=customer_name,
        risk_score=prediction['risk_score'],
        risk_level=RiskLevel(prediction['risk_level']),
        confidence=prediction['confidence'],
        factors=prediction['factors'],
        recommended_credit_limit=prediction['recommended_credit_limit'],
        recommended_payment_terms=prediction['recommended_payment_terms'],
        model_info=ModelInfo(**model.model_info),
        predicted_at=datetime.utcnow(),
    )


@router.post("/credit-risk/batch")
async def batch_credit_risk(customer_ids: list[str], request: Request):
    """Batch credit risk prediction for multiple customers."""
    results = []
    for cid in customer_ids[:50]:
        try:
            result = await predict_credit_risk(cid, request)
            results.append(result)
        except HTTPException:
            results.append({"customer_id": cid, "error": "Failed to predict"})
    return {"predictions": results}
