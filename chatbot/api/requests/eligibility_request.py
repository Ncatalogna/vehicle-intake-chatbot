import uuid
from pydantic import BaseModel

class EligibilityRequest(BaseModel):
    """
    Modelo de solicitud para el chequeo de elegibilidad.
    """
    client_id: uuid.UUID
    vehicle_id: uuid.UUID