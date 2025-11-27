"""
Lead Scoring API endpoints.
"""
from fastapi import APIRouter, Request, HTTPException
from datetime import datetime
import httpx

from ..schemas.predictions import LeadScoreRequest, LeadScoreResponse, ModelInfo
from ..config import get_settings

router = APIRouter()
settings = get_settings()


async def fetch_lead_data(lead_id: str) -> dict:
    """Fetch lead data from Sales service."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.SALES_SERVICE_URL}/api/v1/leads/{lead_id}/",
                timeout=10.0
            )
            if response.status_code == 200:
                return response.json()
    except Exception:
        pass
    return {}


async def fetch_opportunity_data(lead_id: str) -> dict:
    """Fetch opportunity data if lead has been converted."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.SALES_SERVICE_URL}/api/v1/opportunities/?lead_id={lead_id}",
                timeout=10.0
            )
            if response.status_code == 200:
                data = response.json()
                opportunities = data.get('results', [])
                if opportunities:
                    return opportunities[0]
    except Exception:
        pass
    return {}


async def fetch_engagement_data(lead_id: str) -> dict:
    """Fetch engagement/activity data for the lead."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.SALES_SERVICE_URL}/api/v1/activities/?lead_id={lead_id}&limit=10",
                timeout=10.0
            )
            if response.status_code == 200:
                data = response.json()
                activities = data.get('results', [])
                
                if activities:
                    last_activity = activities[0]
                    last_date = last_activity.get('created_at', '')
                    if last_date:
                        try:
                            last_dt = datetime.fromisoformat(last_date.replace('Z', '+00:00'))
                            days_since = (datetime.now(last_dt.tzinfo) - last_dt).days
                        except:
                            days_since = 7
                    else:
                        days_since = 7
                    
                    engagement_score = min(100, len(activities) * 10 + 20)
                else:
                    days_since = 30
                    engagement_score = 10
                
                return {
                    'time_since_last_contact': days_since,
                    'engagement_score': engagement_score,
                    'activity_count': len(activities),
                }
    except Exception:
        pass
    return {'time_since_last_contact': 14, 'engagement_score': 30, 'activity_count': 0}


@router.get("/leads/score/{lead_id}", response_model=LeadScoreResponse)
async def score_lead(lead_id: str, request: Request, recalculate: bool = False):
    """
    Score a lead based on conversion probability.
    
    Returns a score (0-99), priority classification, and recommended actions.
    """
    model_manager = getattr(request.app.state, 'model_manager', None)
    if not model_manager:
        raise HTTPException(status_code=503, detail="Models not loaded")
    
    model = model_manager.get_model('lead_scoring')
    if not model:
        raise HTTPException(status_code=503, detail="Lead scoring model not available")
    
    lead_data = await fetch_lead_data(lead_id)
    opportunity_data = await fetch_opportunity_data(lead_id)
    engagement_data = await fetch_engagement_data(lead_id)
    
    lead_name = lead_data.get('company_name') or lead_data.get('name')
    
    opportunity_value = float(opportunity_data.get('amount', 0) or lead_data.get('estimated_value', 100000) or 100000)
    
    company_size_map = {
        '1-10': 'startup', '11-50': 'small', '51-200': 'medium',
        '201-1000': 'large', '1000+': 'enterprise'
    }
    company_size = company_size_map.get(
        lead_data.get('company_size', ''),
        lead_data.get('tier', 'medium')
    )
    
    features = {
        'lead_source': lead_data.get('source', 'website'),
        'industry': lead_data.get('industry', 'construction'),
        'opportunity_value': opportunity_value,
        'company_size': company_size,
        'engagement_score': engagement_data['engagement_score'],
        'time_since_last_contact': engagement_data['time_since_last_contact'],
    }
    
    prediction = model.predict(features)
    
    return LeadScoreResponse(
        lead_id=lead_id,
        lead_name=lead_name,
        score=prediction['score'],
        conversion_probability=prediction['conversion_probability'],
        priority=prediction['priority'],
        factors=prediction['factors'],
        recommended_actions=prediction['recommended_actions'],
        model_info=ModelInfo(**model.model_info),
        predicted_at=datetime.utcnow(),
    )


@router.post("/leads/batch-score")
async def batch_score_leads(lead_ids: list[str], request: Request):
    """Batch lead scoring for multiple leads."""
    results = []
    for lid in lead_ids[:100]:
        try:
            result = await score_lead(lid, request)
            results.append(result)
        except HTTPException:
            results.append({"lead_id": lid, "error": "Failed to score"})
    
    results.sort(key=lambda x: x.score if hasattr(x, 'score') else 0, reverse=True)
    
    return {"predictions": results}


@router.get("/leads/top-leads")
async def get_top_leads(request: Request, limit: int = 10):
    """Get top-scoring leads (requires leads list from Sales service)."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.SALES_SERVICE_URL}/api/v1/leads/?status=open&limit=50",
                timeout=10.0
            )
            if response.status_code == 200:
                data = response.json()
                leads = data.get('results', [])
                
                scored_leads = []
                for lead in leads:
                    try:
                        score = await score_lead(str(lead['id']), request)
                        scored_leads.append(score)
                    except:
                        pass
                
                scored_leads.sort(key=lambda x: x.score, reverse=True)
                return {"top_leads": scored_leads[:limit]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return {"top_leads": []}
