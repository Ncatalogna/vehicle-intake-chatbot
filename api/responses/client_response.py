import uuid
from datetime import date
from typing import Optional, List
from pydantic import ConfigDict, Field

from .base_response import BaseResponse
from .vehicle_response import VehicleResponse
from entities.client_entity import IdentificationType

class ClientResponse(BaseResponse):
    """
    Modelo de respuesta para un cliente.
    """
    id: uuid.UUID = Field(description="El ID único (UUID) del cliente en el sistema.")
    name: Optional[str] = Field(None, description="El nombre de pila del cliente.")
    last_name: Optional[str] = Field(None, description="El apellido del cliente.")
    birth_date: Optional[date] = Field(None, description="La fecha de nacimiento del cliente (YYYY-MM-DD).")
    documento: Optional[str] = Field(None, description="El número de documento del cliente.")
    documento_type: Optional[IdentificationType] = Field(None, description="El tipo de documento (DNI, CUIT o CUIL).")
    email: Optional[str] = Field(None, description="La dirección de correo electrónico del cliente.")
    phone_number: Optional[str] = Field(None, description="El número de teléfono del cliente.")
    vehicles: List[VehicleResponse] = Field([], description="Una lista de los vehículos asociados a este cliente.")
    
    model_config = ConfigDict(from_attributes=True)