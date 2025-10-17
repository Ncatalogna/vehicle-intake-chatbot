from pydantic import BaseModel, Field
from typing import List

class EligibilityResponse(BaseModel):
    """
    Modelo de respuesta para el chequeo de elegibilidad.
    """
    is_eligible: bool = Field(description="Indica si el cliente y el vehículo son elegibles.")
    message: str = Field(description="Un mensaje resumen del resultado de la evaluación.")
    reasons: List[str] = Field([], description="Una lista de razones por las que no es elegible (si aplica).")