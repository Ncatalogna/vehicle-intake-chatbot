import datetime
from typing import Optional, List, Dict, Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import RunnableSerializable
from pydantic import BaseModel, Field, field_validator

from workflow.orchestrator_state import IdentificationType, NextNode, OrchestratorState, ClientResult
from logger import logger

class ParsedClientData(BaseModel):
    """Esquema para los datos del cliente extraídos."""
    name: Optional[str] = Field(None, description="El nombre de pila del usuario.")
    last_name: Optional[str] = Field(None, description="El apellido del usuario.")
    birth_date: Optional[datetime.date] = Field(None, description="La fecha de nacimiento del usuario en formato YYYY-MM-DD.")
    documento: Optional[str] = Field(None, description="El número de documento del usuario.")
    documento_type: Optional[IdentificationType] = Field(None, description="El tipo de documento (DNI, CUIT o CUIL).")
    email: Optional[str] = Field(None, description="El correo electrónico del usuario.")
    phone_number: Optional[str] = Field(None, description="El número de teléfono del usuario.")

    @field_validator("documento_type", mode="before")
    @classmethod
    def clean_document_type(cls, v: str):
        if isinstance(v, str):
            return v.lower()
        return v

class ValidationResult(BaseModel):
    """Define la salida del agente validador."""
    parsed_data: ParsedClientData = Field(description="Los datos del cliente que se lograron estructurar.")
    base_message: str = Field(description="El mensaje base para el usuario. Debe ser una pregunta por el siguiente dato faltante.")

FIELD_CONFIG = {
    "descriptions": {
        "documento": "número de documento",
        "documento_type": "tipo de documento (DNI, CUIT o CUIL)",
        "name": "nombre",
        "last_name": "apellido",
        "birth_date": "fecha de nacimiento",
        "email": "correo electrónico",
        "phone_number": "número de teléfono"
    },
    "groups": {
        "nombre_group": ["name", "last_name"],
        "documento_group": {"documento", "documento_type"}
    },
    "single_fields": [
        "birth_date",
        "email",
        "phone_number"
    ],
    "priority": [
        "nombre_group",
        "documento_group",
        "birth_date",
        "email",
        "phone_number"
    ]
}

def create_client_validator_agent(
    llm: BaseChatModel,
) -> RunnableSerializable:
    """
    Crea un agente que extrae datos y formula la siguiente pregunta.
    """
    system_prompt_template = (
        "Tu tarea es rellenar los datos del cliente. El 'Mensaje del usuario' es la respuesta a una pregunta sobre el primer dato que falta en la lista.\n\n"
        "**Datos Faltantes (en orden de prioridad)**:\n{missing_fields_list}\n\n"
        "**Instenciones del Usuario**:\n{intent_description}\n\n"
        "**Instrucciones**:\n"
        "1.  Asigna el contenido del 'Mensaje del usuario' al primer campo de la lista de 'Datos Faltantes'.\n"
        "2.  Si puedes extraer otros datos del mensaje, hazlo también.\n"
        "3.  Tras rellenar los datos, formula una pregunta clara en `base_message` para el siguiente dato que falte.\n"
        "4.  Si ya no faltan datos, devuelve un `base_message` vacío."
    )
    
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=system_prompt_template),
            ("user", "Datos actuales del cliente: {current_data}"),
            ("user", "Mensaje del usuario: {message}"),
        ]
    )
    
    structured_llm = llm.with_structured_output(ValidationResult)
    agent = prompt | structured_llm
    return agent

def client_validator_node(
    state: OrchestratorState,
    agent: RunnableSerializable
) -> dict:
    """
    Ejecuta el agente validador con un contexto limpio para evitar errores.
    """
    logger.debug("---WORKER: Validando y Generando Contexto---")
    
    message = state.get("message", "")
    intent_description = state.get("intent_description", "") 
    base_message = state.get("base_message", []) or []

    client_data = state.get("client")
    if not client_data:
        client_data = ClientResult(
            id=None,
            name=None,
            last_name=None,
            birth_date=None,
            documento=None,
            documento_type=None,
            email=None,
            phone_number=None
        )

    current_data = client_data.dict()

    missing_fields_list = []
    ordered_missing_fields = []
    for concept_key in FIELD_CONFIG.get("priority", []):
        if concept_key in FIELD_CONFIG["groups"]:
            for field in FIELD_CONFIG["groups"][concept_key]:
                if not current_data.get(field):
                    ordered_missing_fields.append(field)
        elif concept_key in FIELD_CONFIG["single_fields"]:
            if not current_data.get(concept_key):
                ordered_missing_fields.append(concept_key)

    missing_fields_list = [f"- {FIELD_CONFIG['descriptions'][f]}" for f in ordered_missing_fields]

    try:
        validation_result = agent.invoke({
            "message": message,
            "intent_description": intent_description,
            "current_data": str(current_data),
            "missing_fields_list": "\n".join(missing_fields_list) or "Ninguno"
        })

        extracted_data = validation_result.parsed_data.dict(exclude_unset=True)
        state_update: Dict[str, Any] = {}
        updated_client_data = client_data

        if extracted_data:
            updated_client_data = client_data.copy(update=extracted_data)
            state_update["client"] = updated_client_data
        
        all_fields_present_after_extraction = True
        for field in FIELD_CONFIG["descriptions"].keys():
            if not getattr(updated_client_data, field, None):
                all_fields_present_after_extraction = False
                break
        
        if all_fields_present_after_extraction:
            logger.debug("---WORKER: Todos los datos del cliente recopilados. Preparando confirmación.---")
            confirmation_request = {
                key: str(value) for key, value in updated_client_data.dict().items() if value is not None and key != 'id'
            }
            confirmation_message_parts = [
                f"{FIELD_CONFIG['descriptions'][key]}: {value}"
                for key, value in confirmation_request.items()
            ]
            confirmation_message = "Por favor, confirma si los siguientes datos son correctos:\n" + "\n".join(confirmation_message_parts) + "\n\nResponde 'sí' para confirmar o 'no' para corregir."

            state_update["confirmation_request"] = confirmation_request
            state_update["base_message"] = base_message + [confirmation_message]
            state_update["next_node"] = NextNode.CONFIRM_CLIENT_DATA
        elif validation_result.base_message:
            state_update["base_message"] = base_message + [validation_result.base_message]

    except Exception as e:
        logger.error(f"Error en el validador dinámico: {e}", exc_info=True)
        return {
            "base_message": ["Hubo un problema procesando tu información. Por favor, intenta de nuevo."],
            "next_node": NextNode.GENERATE_RESPONSE
        }

    logger.debug(f"---WORKER: Datos Estructurados -> {state_update} ---")
    if "base_message" in state_update and state_update["base_message"]:
        logger.debug(f"---WORKER: Mensaje Base Generado -> \"{state_update['base_message']}\" ---")

    return state_update