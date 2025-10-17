from datetime import date
from typing import Optional
from pydantic import BaseModel, Field
from entities.client_entity import IdentificationType

class ClientRequest(BaseModel):
    name: str = Field(..., description="El nombre de pila del usuario.")
    last_name: str = Field(..., description="El apellido del usuario.")
    birth_date: date = Field(..., description="La fecha de nacimiento del usuario en formato YYYY-MM-DD.")
    documento: str = Field(..., description="El número de documento del usuario.")
    documento_type: IdentificationType = Field(..., description="El tipo de documento (DNI, CUIT o CUIL).")
    email: str = Field(..., description="El correo electrónico del usuario.")
    phone_number: Optional[str] = Field(None, description="El número de teléfono del usuario.")