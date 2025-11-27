"""
Demand Forecasting API endpoints.
"""
from fastapi import APIRouter, Request, HTTPException
from datetime import datetime, date
from typing import Optional
import httpx

from ..schemas.predictions import DemandForecastRequest, DemandForecastResponse, DemandForecastItem, ModelInfo
from ..config import get_settings

router = APIRouter()
settings = get_settings()


async def fetch_product_data(product_id: str) -> dict:
    """Fetch product data from Inventory service."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.INVENTORY_SERVICE_URL}/api/v1/products/{product_id}/",
                timeout=10.0
            )
            if response.status_code == 200:
                return response.json()
    except Exception:
        pass
    return {}


async def fetch_stock_level(product_id: str, warehouse_id: Optional[str] = None) -> dict:
    """Fetch current stock level for product."""
    try:
        url = f"{settings.INVENTORY_SERVICE_URL}/api/v1/stock/?product_id={product_id}"
        if warehouse_id:
            url += f"&warehouse_id={warehouse_id}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            if response.status_code == 200:
                data = response.json()
                stock_items = data.get('results', [])
                total_stock = sum(float(s.get('quantity', 0) or 0) for s in stock_items)
                return {'current_stock': total_stock}
    except Exception:
        pass
    return {'current_stock': 0}


async def fetch_historical_demand(product_id: str) -> dict:
    """Fetch historical demand data for product."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.INVENTORY_SERVICE_URL}/api/v1/stock/movements/?product_id={product_id}&type=outbound",
                timeout=10.0
            )
            if response.status_code == 200:
                data = response.json()
                movements = data.get('results', [])
                
                if movements:
                    total_demand = sum(float(m.get('quantity', 0) or 0) for m in movements)
                    
                    if len(movements) > 1:
                        dates = [m.get('created_at', '') for m in movements]
                        dates = [d for d in dates if d]
                        if len(dates) >= 2:
                            try:
                                first = datetime.fromisoformat(dates[-1].replace('Z', '+00:00'))
                                last = datetime.fromisoformat(dates[0].replace('Z', '+00:00'))
                                days = max((last - first).days, 1)
                                avg_daily = total_demand / days
                            except:
                                avg_daily = total_demand / max(len(movements), 1)
                        else:
                            avg_daily = total_demand / 30
                    else:
                        avg_daily = float(movements[0].get('quantity', 10) or 10) / 7
                else:
                    avg_daily = 5
                
                return {'avg_daily_demand': avg_daily}
    except Exception:
        pass
    return {'avg_daily_demand': 5}


async def fetch_upcoming_projects_demand(product_id: str) -> int:
    """Estimate demand from upcoming projects."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.PROJECT_SERVICE_URL}/api/v1/projects/?status=planned,active",
                timeout=10.0
            )
            if response.status_code == 200:
                data = response.json()
                projects = data.get('results', [])
                return len(projects)
    except Exception:
        pass
    return 2


@router.get("/inventory/demand-forecast/{product_id}", response_model=DemandForecastResponse)
async def forecast_demand(
    product_id: str,
    request: Request,
    warehouse_id: Optional[str] = None,
    forecast_days: int = 30
):
    """
    Forecast demand for a product.
    
    Returns daily demand predictions, reorder point,
    suggested order quantity, and stockout risk.
    """
    model_manager = getattr(request.app.state, 'model_manager', None)
    if not model_manager:
        raise HTTPException(status_code=503, detail="Models not loaded")
    
    model = model_manager.get_model('demand_forecast')
    if not model:
        raise HTTPException(status_code=503, detail="Demand forecast model not available")
    
    product_data = await fetch_product_data(product_id)
    stock_data = await fetch_stock_level(product_id, warehouse_id)
    historical = await fetch_historical_demand(product_id)
    upcoming_projects = await fetch_upcoming_projects_demand(product_id)
    
    product_name = product_data.get('name')
    
    month = datetime.now().month
    if product_data.get('category', '').lower() in ['cement', 'concrete', 'bricks']:
        if 5 <= month <= 8:
            seasonality = 0.7
        else:
            seasonality = 0.3
    else:
        seasonality = 0.2
    
    lead_time = int(product_data.get('lead_time_days', 7) or 7)
    unit_price = float(product_data.get('price', 100) or 100)
    
    features = {
        'forecast_days': min(max(forecast_days, 7), 180),
        'avg_daily_demand': historical['avg_daily_demand'],
        'seasonality': seasonality,
        'upcoming_projects': upcoming_projects,
        'current_stock': stock_data['current_stock'],
        'lead_time_days': lead_time,
        'unit_price': unit_price,
    }
    
    prediction = model.predict(features)
    
    forecast_items = [
        DemandForecastItem(
            date=date.fromisoformat(item['date']),
            predicted_demand=item['predicted_demand'],
            confidence_lower=item['confidence_lower'],
            confidence_upper=item['confidence_upper'],
        )
        for item in prediction['forecast']
    ]
    
    stockout_date = None
    if prediction['stockout_risk_date']:
        stockout_date = date.fromisoformat(prediction['stockout_risk_date'])
    
    return DemandForecastResponse(
        product_id=product_id,
        product_name=product_name,
        warehouse_id=warehouse_id,
        forecast=forecast_items,
        current_stock=prediction['current_stock'],
        reorder_point=prediction['reorder_point'],
        suggested_order_quantity=prediction['suggested_order_quantity'],
        stockout_risk_date=stockout_date,
        model_info=ModelInfo(**model.model_info),
        predicted_at=datetime.utcnow(),
    )


@router.get("/inventory/low-stock-forecast")
async def get_low_stock_products(request: Request, days_ahead: int = 14):
    """Get products that are predicted to run low within the specified days."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.INVENTORY_SERVICE_URL}/api/v1/products/?status=active",
                timeout=10.0
            )
            if response.status_code == 200:
                data = response.json()
                products = data.get('results', [])
                
                low_stock = []
                for product in products:
                    try:
                        prediction = await forecast_demand(
                            str(product['id']), request, forecast_days=days_ahead
                        )
                        if prediction.stockout_risk_date:
                            low_stock.append({
                                "product_id": prediction.product_id,
                                "product_name": prediction.product_name,
                                "current_stock": prediction.current_stock,
                                "stockout_date": prediction.stockout_risk_date.isoformat(),
                                "suggested_order": prediction.suggested_order_quantity,
                                "reorder_point": prediction.reorder_point,
                            })
                    except:
                        pass
                
                low_stock.sort(key=lambda x: x['stockout_date'])
                return {"low_stock_products": low_stock}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return {"low_stock_products": []}


@router.post("/inventory/optimize-reorder")
async def optimize_reorder(product_ids: list[str], request: Request):
    """Generate optimized reorder recommendations for multiple products."""
    recommendations = []
    
    for pid in product_ids[:50]:
        try:
            forecast = await forecast_demand(pid, request, forecast_days=30)
            if forecast.current_stock <= forecast.reorder_point:
                urgency = "immediate"
            elif forecast.stockout_risk_date:
                days_to_stockout = (forecast.stockout_risk_date - date.today()).days
                urgency = "urgent" if days_to_stockout < 7 else "normal"
            else:
                urgency = "normal"
            
            recommendations.append({
                "product_id": pid,
                "product_name": forecast.product_name,
                "current_stock": forecast.current_stock,
                "reorder_point": forecast.reorder_point,
                "suggested_quantity": forecast.suggested_order_quantity,
                "urgency": urgency,
                "stockout_risk_date": forecast.stockout_risk_date.isoformat() if forecast.stockout_risk_date else None,
            })
        except:
            pass
    
    recommendations.sort(key=lambda x: 0 if x['urgency'] == 'immediate' else 1 if x['urgency'] == 'urgent' else 2)
    
    return {"reorder_recommendations": recommendations}
