from typing import Dict, Any
from langchain_core.language_models import BaseChatModel
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel, Field

from workflow.orchestrator_state import (
    OrchestratorState,
    NextNode,
    VehicleResult,
)
from logger import logger
from workflow.tools.vehicle_tool import vehicle_tool

class AgentResponse(BaseModel):
    """Define la respuesta del agente de confirmación."""
    base_message: str = Field(description="El mensaje para enviar al usuario.")
    clear_data: bool = Field(default=False, description="True si los datos pendientes de confirmación deben ser eliminados.")

def create_vehicle_confirmation_agent(llm: BaseChatModel) -> AgentExecutor:
    """Crea un agente que procesa los datos del vehículo utilizando herramientas."""
    tools = vehicle_tool()

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system",
             "Tu primera tarea es analizar la respuesta del usuario a una solicitud de confirmación de datos del vehículo.\n"
             "1. Si el usuario confirma (responde 'sí', 'correcto', etc.), procede a registrar la información del vehículo usando las herramientas definidas. Necesitarás el 'client_id' del contexto para ello.\n"
             "2. Si el usuario niega (responde 'no', 'incorrecto', etc.), responde con un mensaje amigable pidiéndole que ingrese los datos de nuevo y establece `clear_data` a True.\n"
             "3. Si la respuesta no es clara, pide una aclaración.\n\n"
             "ID del Cliente para asociar el vehículo: {client_id}\n"
             "Datos pendientes de confirmación:\n{confirmation_data}"
            ),
            ("user", "{message}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
    
    agent = create_openai_tools_agent(llm, tools, prompt)
    
    return AgentExecutor(agent=agent, tools=tools, verbose=True, return_intermediate_steps=True)

async def vehicle_confirmation_node(state: OrchestratorState, agent: AgentExecutor) -> dict:
    """
    Invoca al agente de confirmación de vehículo y procesa su respuesta.
    """
    logger.debug("---WORKER: Agente de Confirmación y Procesamiento de Vehículo---")

    message = state.get("message", "")
    client = state.get("client")
    confirmation_request = state.get("confirmation_request")

    if not confirmation_request:
        return {"next_node": NextNode.COLLECT_VEHICLE_DATA}
    
    if not client or not client.id:
        logger.error("Error: No se encontró el ID del cliente para la confirmación del vehículo.")
        return {
            "base_message": ["Ocurrió un error inesperado. No se pudo identificar al cliente para registrar el vehículo."],
            "next_node": NextNode.FALLBACK
        }

    try:
        confirmation_data_str = "\n".join([f"- {k}: {v}" for k, v in confirmation_request.items()])
        response = await agent.ainvoke({
            "message": message,
            "client_id": client.id,
            "confirmation_data": confirmation_data_str
        })
        
        output = response.get("output", "")
        intermediate_steps = response.get("intermediate_steps", [])

        state_update: Dict[str, Any] = {"confirmation_request": None}

        if intermediate_steps:
            logger.debug("---WORKER: Herramientas de vehículo ejecutadas. Actualizando estado.---")
            for step in intermediate_steps:
                tool_output = step[1]
                if isinstance(tool_output, VehicleResult):
                    state_update["vehicle"] = tool_output
            state_update["base_message"] = [output or "Los datos de tu vehículo han sido registrados."]
        else:
            try:
                parsed_response = AgentResponse.model_validate(output)
                state_update["base_message"] = [parsed_response.base_message]
                if parsed_response.clear_data:
                    logger.warning("---WORKER: Usuario negó los datos del vehículo. Limpiando campos.---")
                    state_update["vehicle"] = None # Limpia el objeto vehículo para volver a pedir los datos
            except Exception:
                 state_update["base_message"] = [output]

        return state_update

    except Exception as e:
        logger.error(f"Ocurrió un error en el agente de confirmación de vehículo: {e}", exc_info=True)
        return {"base_message": ["Hubo un problema procesando tu respuesta. Por favor, intenta de nuevo."]}