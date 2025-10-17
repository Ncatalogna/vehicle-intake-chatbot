import uuid
from datetime import date
from typing import Optional, List

from .base_response import BaseResponse
from .vehicle_response import VehicleResponse
from workflow.orchestrator_state import IdentificationType

class ClientResponse(BaseResponse):
    id: uuid.UUID
    name: Optional[str]
    last_name: Optional[str]
    birth_date: Optional[date]
    documento: Optional[str]
    documento_type: Optional[IdentificationType]
    email: Optional[str]
    phone_number: Optional[str]
    vehicles: List[VehicleResponse]