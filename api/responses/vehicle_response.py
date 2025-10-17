import uuid
from pydantic import Field, ConfigDict

from .base_response import BaseResponse

class VehicleResponse(BaseResponse):
    """
    Modelo de respuesta para un vehículo.
    """
    id: uuid.UUID = Field(description="El ID único (UUID) del vehículo en el sistema.")
    license_plate: str = Field(description="La patente (matrícula) única del vehículo.")
    brand: str = Field(description="La marca del vehículo (ej: Ford, Toyota, etc.).")
    model: str = Field(description="El modelo específico del vehículo (ej: Focus, Corolla, etc.).")
    year: int = Field(description="El año de fabricación del vehículo.")
    mileage: int = Field(description="El kilometraje actual del vehículo.")
    client_id: uuid.UUID = Field(description="El ID único (UUID) del cliente al que pertenece el vehículo.")

    model_config = ConfigDict(from_attributes=True)