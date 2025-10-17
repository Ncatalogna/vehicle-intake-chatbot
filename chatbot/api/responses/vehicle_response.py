import uuid
from .base_response import BaseResponse

class VehicleResponse(BaseResponse):
    id: uuid.UUID
    license_plate: str | None
    brand: str | None
    model: str | None
    year: int | None
    mileage: int | None