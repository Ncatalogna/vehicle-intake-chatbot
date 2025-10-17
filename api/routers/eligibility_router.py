from uuid import UUID
from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from services.eligibility_service import EligibilityService
from responses.eligibility_response import EligibilityResponse

router = APIRouter(prefix="/eligibility", tags=["Eligibility"])

def get_eligibility_service(db: AsyncSession = Depends(get_db)) -> EligibilityService:
    return EligibilityService(db)

@router.post("/check", response_model=EligibilityResponse)
async def check_eligibility(
    client_id: UUID = Body(..., embed=True, description="ID del cliente a evaluar."),
    vehicle_id: UUID = Body(..., embed=True, description="ID del vehículo a evaluar."),
    service: EligibilityService = Depends(get_eligibility_service)
):
    """
    Evalúa si un cliente y su vehículo son elegibles según las reglas de negocio.
    """
    return await service.check_eligibility(client_id, vehicle_id)