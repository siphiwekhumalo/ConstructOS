"""
Predictive Maintenance API endpoints.
"""
from fastapi import APIRouter, Request, HTTPException
from datetime import datetime, date
import httpx

from ..schemas.predictions import MaintenanceRiskRequest, MaintenanceRiskResponse, RiskLevel, ModelInfo
from ..config import get_settings

router = APIRouter()
settings = get_settings()


async def fetch_equipment_data(equipment_id: str) -> dict:
    """Fetch equipment data from Inventory service."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.INVENTORY_SERVICE_URL}/api/v1/equipment/{equipment_id}/",
                timeout=10.0
            )
            if response.status_code == 200:
                return response.json()
    except Exception:
        pass
    return {}


async def fetch_maintenance_history(equipment_id: str) -> dict:
    """Fetch maintenance history for equipment."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.COMPLIANCE_SERVICE_URL}/api/v1/inspections/?equipment_id={equipment_id}&type=maintenance",
                timeout=10.0
            )
            if response.status_code == 200:
                data = response.json()
                inspections = data.get('results', [])
                
                failure_count = sum(1 for i in inspections if i.get('result') == 'failed')
                
                if inspections:
                    last_service = inspections[0]
                    last_date = last_service.get('inspection_date', '')
                    if last_date:
                        try:
                            last_dt = datetime.fromisoformat(last_date.replace('Z', '+00:00'))
                            days_since = (datetime.now(last_dt.tzinfo) - last_dt).days
                        except:
                            days_since = 30
                    else:
                        days_since = 30
                else:
                    days_since = 60
                
                return {
                    'failure_history_count': failure_count,
                    'days_since_last_service': days_since,
                    'total_inspections': len(inspections),
                }
    except Exception:
        pass
    return {'failure_history_count': 0, 'days_since_last_service': 30, 'total_inspections': 0}


@router.get("/equipment/maintenance-risk/{equipment_id}", response_model=MaintenanceRiskResponse)
async def predict_maintenance_risk(
    equipment_id: str,
    request: Request,
    days_ahead: int = 30
):
    """
    Predict maintenance needs for equipment.
    
    Returns failure probability, recommended maintenance date,
    and parts that may be needed.
    """
    model_manager = getattr(request.app.state, 'model_manager', None)
    if not model_manager:
        raise HTTPException(status_code=503, detail="Models not loaded")
    
    model = model_manager.get_model('maintenance')
    if not model:
        raise HTTPException(status_code=503, detail="Maintenance model not available")
    
    equipment_data = await fetch_equipment_data(equipment_id)
    maintenance_history = await fetch_maintenance_history(equipment_id)
    
    equipment_name = equipment_data.get('name')
    
    purchase_date = equipment_data.get('purchase_date') or equipment_data.get('acquired_date')
    if purchase_date:
        try:
            purchase_dt = datetime.fromisoformat(purchase_date.replace('Z', '+00:00'))
            age_months = (datetime.now(purchase_dt.tzinfo) - purchase_dt).days / 30
        except:
            age_months = 24
    else:
        age_months = 24
    
    operating_hours = float(equipment_data.get('operating_hours', 0) or 0)
    last_service_hours = float(equipment_data.get('last_service_hours', 0) or 0)
    hours_since_service = operating_hours - last_service_hours
    
    service_intervals = {
        'crane': 250, 'excavator': 300, 'loader': 400,
        'generator': 500, 'compressor': 600, 'general': 500
    }
    equipment_type = equipment_data.get('type', equipment_data.get('category', 'general'))
    if equipment_type:
        equipment_type = equipment_type.lower()
    else:
        equipment_type = 'general'
    service_interval = service_intervals.get(equipment_type, 500)
    
    condition_score = float(equipment_data.get('condition_score', 75) or 75)
    
    if maintenance_history['days_since_last_service'] < 30:
        hours_since_service = min(hours_since_service, maintenance_history['days_since_last_service'] * 8)
    
    features = {
        'equipment_age_months': age_months,
        'hours_since_last_service': max(hours_since_service, 0),
        'service_interval_hours': service_interval,
        'failure_history_count': maintenance_history['failure_history_count'],
        'current_condition_score': condition_score,
        'equipment_type': equipment_type,
        'days_ahead': days_ahead,
    }
    
    prediction = model.predict(features)
    
    return MaintenanceRiskResponse(
        equipment_id=equipment_id,
        equipment_name=equipment_name,
        failure_probability=prediction['failure_probability'],
        risk_level=RiskLevel(prediction['risk_level']),
        estimated_remaining_life_days=prediction['estimated_remaining_life_days'],
        recommended_maintenance_date=date.fromisoformat(prediction['recommended_maintenance_date']),
        maintenance_type=prediction['maintenance_type'],
        estimated_downtime_hours=prediction['estimated_downtime_hours'],
        parts_needed=prediction['parts_needed'],
        model_info=ModelInfo(**model.model_info),
        predicted_at=datetime.utcnow(),
    )


@router.get("/equipment/needs-maintenance")
async def get_equipment_needing_maintenance(request: Request, days_ahead: int = 14):
    """Get all equipment that will need maintenance within the specified days."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.INVENTORY_SERVICE_URL}/api/v1/equipment/?status=active",
                timeout=10.0
            )
            if response.status_code == 200:
                data = response.json()
                equipment_list = data.get('results', [])
                
                needs_maintenance = []
                for eq in equipment_list:
                    try:
                        prediction = await predict_maintenance_risk(
                            str(eq['id']), request, days_ahead
                        )
                        if prediction.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                            needs_maintenance.append(prediction)
                    except:
                        pass
                
                needs_maintenance.sort(key=lambda x: x.failure_probability, reverse=True)
                return {"equipment_needing_maintenance": needs_maintenance}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return {"equipment_needing_maintenance": []}


@router.post("/equipment/schedule-maintenance")
async def schedule_maintenance(equipment_id: str, request: Request):
    """Generate a maintenance schedule recommendation for equipment."""
    prediction = await predict_maintenance_risk(equipment_id, request, days_ahead=90)
    
    return {
        "equipment_id": equipment_id,
        "equipment_name": prediction.equipment_name,
        "recommended_date": prediction.recommended_maintenance_date,
        "maintenance_type": prediction.maintenance_type,
        "estimated_duration_hours": prediction.estimated_downtime_hours,
        "parts_to_order": prediction.parts_needed,
        "urgency": prediction.risk_level.value,
    }
