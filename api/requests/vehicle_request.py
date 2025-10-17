from uuid import UUID
from pydantic import BaseModel, Field

class VehicleRequest(BaseModel):
    license_plate: str = Field(..., description="Patente del vehículo")
    brand: str = Field(..., description="Marca del vehículo")
    model: str = Field(..., description="Modelo del vehículo")
    year: int = Field(..., description="Año del vehículo")
    mileage: int = Field(..., description="Kilometraje del vehículo")
    client_id: UUID = Field(..., description="ID del cliente propietario del vehículo")