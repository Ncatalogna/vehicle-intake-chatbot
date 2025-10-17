import datetime
import enum
import uuid
from typing import Dict, Literal, List, Optional, TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

from pydantic import BaseModel, Field

## Identificación
class IdentificationType(enum.Enum):
    DNI = "dni"
    CUIT = "cuit"
    CUIL = "cuil"

## Contacto
class ContactType(enum.Enum):
    EMAIL = "email"
    PHONE = "phone"

## Cliente
class ClientResult(BaseModel):
    id: Optional[uuid.UUID] = Field(None, description="El ID único del cliente en el sistema.")
    name: Optional[str] = Field(None, description="El nombre de pila del usuario.")
    last_name: Optional[str] = Field(None, description="El apellido del usuario.")
    birth_date: Optional[datetime.date] = Field(None, description="La fecha de nacimiento del usuario en formato YYYY-MM-DD.")
    documento: Optional[str] = Field(None, description="El número de documento del usuario.")
    documento_type: Optional[IdentificationType] = Field(None, description="El tipo de documento (DNI, CUIT o CUIL).")
    email: Optional[str] = Field(None, description="El correo electrónico del usuario.")
    phone_number: Optional[str] = Field(None, description="El número de teléfono del usuario.")

## Vehículo
class VehicleResult(BaseModel):
    id: Optional[uuid.UUID] = Field(None, description="El ID único del vehículo en el sistema.")
    license_plate: Optional[str] = Field(None, description="La patente del vehículo.")
    brand: Optional[str] = Field(None, description="La marca del vehículo.")
    model: Optional[str] = Field(None, description="El modelo del vehículo.")
    year: Optional[int] = Field(None, description="El año de fabricación del vehículo.")
    mileage: Optional[int] = Field(None, description="El kilometraje del vehículo.")

class NextNode(str, enum.Enum):
    """Define los posibles siguientes pasos que el supervisor puede decidir."""
    COLLECT_CLIENT_DATA = "collect_client_data"
    CONFIRM_CLIENT_DATA = "confirm_client_data"
    COLLECT_VEHICLE_DATA = "collect_vehicle_data"
    CONFIRM_VEHICLE_DATA = "confirm_vehicle_data"
    CHECK_ELIGIBILITY = "check_eligibility"
    GENERATE_RESPONSE = "generate_response"
    FALLBACK = "fallback"

class OrchestratorState(TypedDict, total=False):
    """
    El estado unificado para todo el chatbot.
    """
    # --- Mensajes ---
    message: BaseMessage
    messages: Annotated[List[BaseMessage], add_messages]

    # --- Datos ---
    client: Optional[ClientResult]
    vehicle: Optional[VehicleResult]

    # --- Nuevo campo para la confirmación de datos ---
    confirmation_request: Optional[Dict[str, str]]
    
    # Respuesta del validador, necesaria para el enrutamiento
    validator_response: Optional[dict]
    
    # Descripcion de la intencionalidad del usuario
    intent_description: Optional[str]

    # El usuario fue notificado de su elegibilidad
    notify_elegibility: Optional[bool]

    # Campo para almacenar la lista de datos crudos del supervisor
    raw_extracted_data: Optional[List[str]]

    # MENSAJE DE CONTEXTO PARA EL GENERADOR DE RESPUESTAS
    base_message: Optional[List[str]]

    # Indicador para la primera ejecución del supervisor
    is_first_run: Optional[bool]

    next_node: Literal[
            "call_tool", 
            NextNode.COLLECT_CLIENT_DATA, 
            NextNode.CONFIRM_CLIENT_DATA,
            NextNode.COLLECT_VEHICLE_DATA,
            NextNode.CONFIRM_VEHICLE_DATA,
            NextNode.CHECK_ELIGIBILITY,
            NextNode.GENERATE_RESPONSE,
            NextNode.FALLBACK,
            "__end__",
            "continue",
        ]
