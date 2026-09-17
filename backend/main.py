from typing import Optional, List, Dict, Any
from fastapi import FastAPI, Query, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.services.data_service import DataService
from backend.services.recommendation_service import RecommendationService

# Initialize FastAPI App
app = FastAPI(
    title="EnergiQ Backend API",
    description="AI-Based Energy Consumption Intelligence & Optimization System API for Hackathon",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for Streamlit / Frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instantiate Services
data_service = DataService()
recommendation_service = RecommendationService(data_service)


# Response Pydantic Models for Documentation
class SummaryResponse(BaseModel):
    total_energy_kwh: float = Field(..., description="Total historical energy consumption in kWh")
    estimated_cost: float = Field(..., description="Estimated cost based on energy tariff")
    active_anomalies: int = Field(..., description="Number of active abnormal energy events")
    predicted_next_day_kwh: float = Field(..., description="Forecasted next-day energy consumption in kWh")
    estimated_co2_kg: float = Field(..., description="Estimated CO2 emission footprint in kg")
    tariff_rate_kwh: Optional[float] = Field(None, description="Applied tariff rate per kWh")
    co2_factor_kg_per_kwh: Optional[float] = Field(None, description="Applied CO2 factor per kWh")


class ConsumptionRecord(BaseModel):
    timestamp: Optional[str] = Field(None, description="Timestamp of consumption entry")
    building: str = Field(..., description="Building identifier")
    room: str = Field(..., description="Room identifier")
    equipment: Optional[str] = Field(None, description="Equipment/appliance name")
    power_kw: Optional[float] = Field(None, description="Power in kilowatts")
    energy_kwh: Optional[float] = Field(None, description="Energy in kilowatt-hours")


class ConsumptionResponse(BaseModel):
    data: List[Dict[str, Any]] = Field(..., description="List of consumption data records")


class AnomalyRecord(BaseModel):
    timestamp: Optional[str] = Field(None, description="Timestamp of anomaly event")
    building: str = Field(..., description="Building identifier")
    room: str = Field(..., description="Room identifier")
    equipment: Optional[str] = Field(None, description="Equipment identifier")
    actual_power_kw: Optional[float] = Field(None, description="Actual measured power in kW")
    normal_power_kw: Optional[float] = Field(None, description="Expected normal power in kW")
    status: str = Field(..., description="Anomaly status (e.g. ANOMALY or NORMAL)")
    anomaly_score: Optional[float] = Field(None, description="Anomaly detection model score")


class AnomalyResponse(BaseModel):
    anomalies: List[Dict[str, Any]] = Field(..., description="List of detected anomaly records")


class PredictionRecord(BaseModel):
    date: Optional[str] = Field(None, description="Prediction target date or timestamp")
    location: str = Field(..., description="Building or location identifier")
    room: str = Field(..., description="Room identifier")
    predicted_energy_kwh: float = Field(..., description="Forecasted energy consumption in kWh")


class PredictionResponse(BaseModel):
    predictions: List[Dict[str, Any]] = Field(..., description="List of energy prediction records")


class EquipmentRoom(BaseModel):
    name: str
    equipment: List[str]


class BuildingHierarchy(BaseModel):
    name: str
    rooms: List[EquipmentRoom]


class RoomsResponse(BaseModel):
    buildings: List[BuildingHierarchy]


class RecommendationItem(BaseModel):
    building: str
    room: str
    equipment: str
    priority: str = Field(..., description="Recommendation priority: HIGH, MEDIUM, or LOW")
    message: str = Field(..., description="Actionable recommendation message")


class RecommendationsResponse(BaseModel):
    recommendations: List[RecommendationItem]


# Endpoints

@app.get("/", summary="Root Status Check", tags=["System"])
def read_root():
    """Health check endpoint providing backend metadata."""
    return {
        "status": "online",
        "service": "EnergiQ Backend API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get(
    "/summary",
    response_model=SummaryResponse,
    summary="Get Energy KPI Summary",
    tags=["KPIs & Summary"]
)
def get_summary(
    tariff: Optional[float] = Query(None, description="Override electricity tariff per kWh"),
    co2_factor: Optional[float] = Query(None, description="Override CO2 factor per kWh"),
):
    """
    Returns high-level KPI summary required by frontend dashboard:
    - total_energy_kwh
    - estimated_cost
    - active_anomalies
    - predicted_next_day_kwh
    - estimated_co2_kg
    """
    kwargs = {}
    if tariff is not None:
        if tariff < 0:
            raise HTTPException(status_code=400, detail="Tariff rate cannot be negative.")
        kwargs["tariff_per_kwh"] = tariff
    if co2_factor is not None:
        if co2_factor < 0:
            raise HTTPException(status_code=400, detail="CO2 factor cannot be negative.")
        kwargs["co2_per_kwh"] = co2_factor

    return data_service.get_summary_metrics(**kwargs)


@app.get(
    "/consumption",
    response_model=ConsumptionResponse,
    summary="Get Energy Consumption Data",
    tags=["Consumption"]
)
def get_consumption(
    building: Optional[str] = Query(None, description="Filter by building name"),
    room: Optional[str] = Query(None, description="Filter by room name"),
    equipment: Optional[str] = Query(None, description="Filter by equipment name"),
):
    """
    Returns historical energy consumption logs with optional filters.
    """
    try:
        data = data_service.get_consumption_data(
            building=building, room=room, equipment=equipment
        )
        return {"data": data}
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Consumption data missing: {str(e)}"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid consumption data format: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading consumption data: {str(e)}"
        )


@app.get(
    "/anomalies",
    response_model=AnomalyResponse,
    summary="Get Abnormal Consumption Events",
    tags=["Anomalies"]
)
def get_anomalies(
    building: Optional[str] = Query(None, description="Filter by building name"),
    room: Optional[str] = Query(None, description="Filter by room name"),
):
    """
    Returns detected abnormal energy consumption records.
    """
    try:
        anomalies = data_service.get_anomaly_data(building=building, room=room)
        return {"anomalies": anomalies}
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Anomaly dataset missing: {str(e)}"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid anomaly dataset format: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading anomaly data: {str(e)}"
        )


@app.get(
    "/prediction",
    response_model=PredictionResponse,
    summary="Get Future Energy Predictions",
    tags=["Predictions"]
)
def get_predictions(
    building: Optional[str] = Query(None, description="Filter by building name"),
    room: Optional[str] = Query(None, description="Filter by room name"),
):
    """
    Returns energy consumption predictions generated by AI/ML models.
    """
    try:
        predictions = data_service.get_prediction_data(building=building, room=room)
        return {"predictions": predictions}
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prediction dataset missing: {str(e)}"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid prediction dataset format: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading prediction data: {str(e)}"
        )


@app.get(
    "/rooms",
    response_model=RoomsResponse,
    summary="Get Building & Room Hierarchy",
    tags=["Metadata"]
)
def get_rooms():
    """
    Returns hierarchical building, room, and equipment mapping derived from datasets.
    """
    return data_service.get_room_hierarchy()


@app.get(
    "/recommendations",
    response_model=RecommendationsResponse,
    summary="Get Energy Optimization Recommendations",
    tags=["Recommendations"]
)
def get_recommendations():
    """
    Returns rule-based energy savings recommendations based on consumption and anomalies.
    """
    recs = recommendation_service.generate_recommendations()
    return {"recommendations": recs}
