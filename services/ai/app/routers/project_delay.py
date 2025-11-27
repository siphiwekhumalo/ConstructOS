"""
Project Delay Prediction API endpoints.
"""
from fastapi import APIRouter, Request, HTTPException
from datetime import datetime
import httpx

from ..schemas.predictions import ProjectDelayRequest, ProjectDelayResponse, RiskLevel, ModelInfo
from ..config import get_settings

router = APIRouter()
settings = get_settings()


async def fetch_project_data(project_id: str) -> dict:
    """Fetch project data from Project service."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.PROJECT_SERVICE_URL}/api/v1/projects/{project_id}/",
                timeout=10.0
            )
            if response.status_code == 200:
                return response.json()
    except Exception:
        pass
    return {}


async def fetch_resource_data(project_id: str) -> dict:
    """Fetch resource utilization data."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.PROJECT_SERVICE_URL}/api/v1/projects/{project_id}/resources/",
                timeout=10.0
            )
            if response.status_code == 200:
                data = response.json()
                resources = data.get('results', [])
                if resources:
                    total_capacity = sum(r.get('capacity', 100) for r in resources)
                    total_allocated = sum(r.get('allocated', 80) for r in resources)
                    utilization = (total_allocated / max(total_capacity, 1)) * 100
                else:
                    utilization = 75
                return {'resource_utilization': utilization}
    except Exception:
        pass
    return {'resource_utilization': 75}


async def fetch_weather_risk(location: str) -> float:
    """Estimate weather risk based on location and season."""
    month = datetime.now().month
    
    if 5 <= month <= 8:
        base_risk = 0.15
    elif month in [11, 12, 1, 2]:
        base_risk = 0.35
    else:
        base_risk = 0.25
    
    if location:
        location_lower = location.lower()
        if 'cape' in location_lower:
            if 5 <= month <= 8:
                base_risk += 0.2
        elif 'gauteng' in location_lower or 'johannesburg' in location_lower:
            if 10 <= month <= 3:
                base_risk += 0.15
    
    return min(base_risk, 0.8)


@router.get("/projects/delay-risk/{project_id}", response_model=ProjectDelayResponse)
async def predict_project_delay(project_id: str, request: Request, milestone_id: str = None):
    """
    Predict delay risk for a project.
    
    Returns delay probability, expected delay days, risk factors,
    and mitigation suggestions.
    """
    model_manager = getattr(request.app.state, 'model_manager', None)
    if not model_manager:
        raise HTTPException(status_code=503, detail="Models not loaded")
    
    model = model_manager.get_model('project_delay')
    if not model:
        raise HTTPException(status_code=503, detail="Project delay model not available")
    
    project_data = await fetch_project_data(project_id)
    resource_data = await fetch_resource_data(project_id)
    
    project_name = project_data.get('name')
    location = project_data.get('location', project_data.get('site_address', ''))
    weather_risk = await fetch_weather_risk(location)
    
    current_progress = float(project_data.get('progress', 50) or 50)
    
    start_date = project_data.get('start_date')
    end_date = project_data.get('end_date') or project_data.get('due_date')
    
    if start_date and end_date:
        try:
            start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            now = datetime.now(start.tzinfo)
            
            total_days = (end - start).days
            elapsed_days = (now - start).days
            days_remaining = max((end - now).days, 1)
            
            if total_days > 0:
                scheduled_progress = (elapsed_days / total_days) * 100
            else:
                scheduled_progress = current_progress
        except:
            days_remaining = 30
            scheduled_progress = current_progress
    else:
        days_remaining = 30
        scheduled_progress = current_progress
    
    complexity_factors = {
        'infrastructure': 8, 'commercial': 7, 'industrial': 7,
        'residential': 5, 'renovation': 6, 'maintenance': 4
    }
    project_type = project_data.get('type', project_data.get('category', 'commercial'))
    complexity = complexity_factors.get(project_type.lower() if project_type else 'commercial', 6)
    
    features = {
        'project_complexity': complexity,
        'resource_utilization': resource_data['resource_utilization'],
        'weather_risk': weather_risk,
        'current_progress': current_progress,
        'scheduled_progress': scheduled_progress,
        'days_remaining': days_remaining,
        'historical_delay_rate': 0.3,
    }
    
    prediction = model.predict(features)
    
    return ProjectDelayResponse(
        project_id=project_id,
        project_name=project_name,
        delay_probability=prediction['delay_probability'],
        expected_delay_days=prediction['expected_delay_days'],
        risk_level=RiskLevel(prediction['risk_level']),
        risk_factors=prediction['risk_factors'],
        mitigation_suggestions=prediction['mitigation_suggestions'],
        model_info=ModelInfo(**model.model_info),
        predicted_at=datetime.utcnow(),
    )


@router.get("/projects/at-risk")
async def get_at_risk_projects(request: Request, threshold: float = 0.5):
    """Get all projects with delay probability above threshold."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.PROJECT_SERVICE_URL}/api/v1/projects/?status=active",
                timeout=10.0
            )
            if response.status_code == 200:
                data = response.json()
                projects = data.get('results', [])
                
                at_risk = []
                for project in projects:
                    try:
                        prediction = await predict_project_delay(str(project['id']), request)
                        if prediction.delay_probability >= threshold:
                            at_risk.append(prediction)
                    except:
                        pass
                
                at_risk.sort(key=lambda x: x.delay_probability, reverse=True)
                return {"at_risk_projects": at_risk}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return {"at_risk_projects": []}
