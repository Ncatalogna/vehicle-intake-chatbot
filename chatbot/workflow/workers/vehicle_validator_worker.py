from typing import Optional, List, Dict, Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import RunnableSerializable
from pydantic import BaseModel, Field

from workflow.orchestrator_state import NextNode, OrchestratorState, VehicleResult
from logger import logger

class ParsedVehicleData(BaseModel):
    """Esquema para los datos del vehículo extraídos."""
    license_plate: Optional[str] = Field(None, description="La patente del vehículo.")
    brand: Optional[str] = Field(None, description="La marca del vehículo.")
    model: Optional[str] = Field(None, description="El modelo del vehículo.")
    year: Optional[int] = Field(None, description="El año de fabricación del vehículo.")
    mileage: Optional[int] = Field(None, description="El kilometraje del vehículo.")

class ValidationResult(BaseModel):
    """Define la salida del agente validador."""
    parsed_data: ParsedVehicleData = Field(description="Los datos del vehículo que se lograron estructurar.")
    base_message: str = Field(description="El mensaje base para el usuario. Debe ser una pregunta por el siguiente dato faltante.")

FIELD_CONFIG = {
    "descriptions": {
        "license_plate": "patente",
        "brand": "marca",
        "model": "modelo",
        "year": "año",
        "mileage": "kilometraje"
    },
    "priority": [
        "license_plate",
        "brand",
        "model",
        "year",
        "mileage"
    ]
}

def create_vehicle_validator_agent(
    llm: BaseChatModel,
) -> RunnableSerializable:
    """
    Crea un agente que extrae datos del vehículo y formula la siguiente pregunta.
    """
    system_prompt_template = (
        "Tu tarea es rellenar los datos del vehículo. El 'Mensaje del usuario' es la respuesta a una pregunta sobre el primer dato que falta en la lista.\n\n"
        "**Datos Faltantes (en orden de prioridad)**:\n{missing_fields_list}\n\n"
        "**Instenciones del Usuario**:\n{intent_description}\n\n"
        "**Instrucciones**:\n"
        "1.  Asigna el contenido del 'Mensaje del usuario' al primer campo de la lista de 'Datos Faltantes'.\n"
        "2.  Si puedes extraer otros datos del mensaje, hazlo también. No elimines datos existentes que no estén en el mensaje actual.\n"
        "3.  Tras rellenar los datos, formula una pregunta clara en `base_message` para el siguiente dato que falte.\n"
        "4.  Si ya no faltan datos, devuelve un `base_message` vacío."
    )
    
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=system_prompt_template),
            ("user", "Datos actuales del vehículo: {current_data}"),
            ("user", "Mensaje del usuario: {message}"),
        ]
    )
    
    structured_llm = llm.with_structured_output(ValidationResult)
    agent = prompt | structured_llm
    return agent

def vehicle_validator_node(
    state: OrchestratorState,
    agent: RunnableSerializable
) -> dict:
    """
    Ejecuta el agente validador de vehículos.
    """
    logger.debug("---WORKER: Validando Datos del Vehículo---")
    
    message = state.get("message", "")
    intent_description = state.get("intent_description", "") 
    base_message = state.get("base_message", []) or []

    vehicle_data = state.get("vehicle")
    if not vehicle_data:
        vehicle_data = VehicleResult(
            id=None,
            license_plate=None,
            brand=None,
            model=None,
            year=None,
            mileage=None
        )

    current_data = vehicle_data.model_dump()

    missing_fields_list = []
    for field in FIELD_CONFIG.get("priority", []):
        if not current_data.get(field):
            description = FIELD_CONFIG["descriptions"][field]
            missing_fields_list.append(f"- {description}")

    try:
        validation_result = agent.invoke({
            "message": message,
            "intent_description": intent_description,
            "current_data": str(current_data),
            "missing_fields_list": "\n".join(missing_fields_list) or "Ninguno"
        })

        extracted_data = validation_result.parsed_data.model_dump(exclude_unset=True)
        state_update: Dict[str, Any] = {}
        updated_vehicle_data = vehicle_data

        if extracted_data:
            updated_vehicle_data = vehicle_data.copy(update=extracted_data)
            state_update["vehicle"] = updated_vehicle_data
        
        all_fields_present_after_extraction = True
        for field in FIELD_CONFIG["descriptions"].keys():
            if getattr(updated_vehicle_data, field, None) is None:
                all_fields_present_after_extraction = False
                break
        
        if all_fields_present_after_extraction:
            logger.debug("---WORKER: Todos los datos del vehículo recopilados. Preparando confirmación.---")
            confirmation_request = {
                key: str(value) for key, value in updated_vehicle_data.model_dump().items() if value is not None and key != 'id'
            }
            confirmation_message_parts = [
                f"{FIELD_CONFIG['descriptions'][key]}: {value}"
                for key, value in confirmation_request.items()
            ]
            confirmation_message = "Por favor, confirma si los siguientes datos del vehículo son correctos:\n" + "\n".join(confirmation_message_parts) + "\n\nResponde 'sí' para confirmar o 'no' para corregir."

            state_update["confirmation_request"] = confirmation_request
            state_update["base_message"] = base_message + [confirmation_message]
            state_update["next_node"] = NextNode.CONFIRM_VEHICLE_DATA
        elif validation_result.base_message:
            state_update["base_message"] = base_message + [validation_result.base_message]

    except Exception as e:
        logger.error(f"Error en el validador de vehículo: {e}", exc_info=True)
        return {
            "base_message": ["Hubo un problema procesando la información de tu vehículo. Por favor, intenta de nuevo."],
            "next_node": NextNode.GENERATE_RESPONSE
        }

    logger.debug(f"---WORKER: Datos de Vehículo Estructurados -> {state_update} ---")
    if "base_message" in state_update and state_update["base_message"]:
        logger.debug(f"---WORKER: Mensaje Base de Vehículo Generado -> \"{state_update['base_message']}\" ---")

    return state_update