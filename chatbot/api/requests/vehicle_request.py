from uuid import UUID
from pydantic import BaseModel

class VehicleRequest(BaseModel):
    client_id: UUID
    license_plate: str
    brand: str
    model: str
    year: int
    mileage: int