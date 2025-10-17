from datetime import datetime
from pydantic import BaseModel

class BaseResponse(BaseModel):
    """
    Modelo base para las respuestas de la API.
    """
    created_at: datetime
    updated_at: datetime