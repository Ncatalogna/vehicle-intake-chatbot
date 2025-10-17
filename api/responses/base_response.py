from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class BaseResponse(BaseModel):
    """
    Modelo base para las respuestas de la API.
    """
    created_at: datetime = Field(description="Fecha y hora de creación del registro.")
    updated_at: datetime = Field(description="Fecha y hora de la última actualización del registro.")
    
    model_config = ConfigDict(from_attributes=True)