from pydantic import BaseModel, Field
from typing import List

class EligibilityResponse(BaseModel):
    """
    Modelo de respuesta para el chequeo de elegibilidad.
    """
    is_eligible: bool
    message: str
    reasons: List[str]