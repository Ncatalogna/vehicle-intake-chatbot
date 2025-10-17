from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from services.vehicle_service import VehicleService
from requests.vehicle_request import VehicleRequest
from responses.vehicle_response import VehicleResponse

router = APIRouter(prefix="/vehicles", tags=["Vehicles"])

def get_vehicle_service(db: AsyncSession = Depends(get_db)) -> VehicleService:
    return VehicleService(db)

@router.post("/", response_model=VehicleResponse, status_code=201)
async def create_vehicle(
    vehicle_data: VehicleRequest,
    service: VehicleService = Depends(get_vehicle_service)
):
    return await service.create_vehicle(vehicle_data)

@router.get("/{vehicle_id}", response_model=VehicleResponse)
async def get_vehicle(
    vehicle_id: UUID, service: VehicleService = Depends(get_vehicle_service)
):
    vehicle = await service.get_vehicle_by_id(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle

@router.get("/client/{client_id}", response_model=List[VehicleResponse])
async def get_client_vehicles(
    client_id: UUID, service: VehicleService = Depends(get_vehicle_service)
):
    return await service.get_vehicles_for_client(client_id)