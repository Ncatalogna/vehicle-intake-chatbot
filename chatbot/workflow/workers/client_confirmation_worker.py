from typing import Dict, Any
from langchain_core.language_models import BaseChatModel
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel, Field

from workflow.orchestrator_state import (
    OrchestratorState,
    NextNode,
    ClientResult,
)
from logger import logger
from workflow.tools.client_tool import client_tool

class AgentResponse(BaseModel):
    """Define la respuesta del agente de confirmación."""
    base_message: str = Field(description="El mensaje para enviar al usuario.")
    clear_data: bool = Field(default=False, description="True si los datos pendientes de confirmación deben ser eliminados.")

def create_client_confirmation_agent(llm: BaseChatModel) -> AgentExecutor:
    """Crea un agente que procesa los datos del cliente utilizando herramientas."""
    tools = client_tool()

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", 
             "Tu primera tarea es analizar la respuesta del usuario a una solicitud de confirmación de datos.\n"
             "1. Si el usuario confirma (responde 'sí', 'correcto', etc.), procede a registrar su información usando las herramientas definidas en el contexto.\n"
             "2. Si el usuario niega (responde 'no', 'incorrecto', etc.), responde con un mensaje amigable pidiéndole que ingrese los datos de nuevo y establece `clear_data` a True.\n"
             "3. Si la respuesta no es clara, pide una aclaración.\n\n"
             "4. Si el usuario confirma, llamar a la tool correspondiente para insertar o actualizar los datos.\n"
             "Datos pendientes de confirmación:\n{confirmation_data}"
            ),
            ("user", "{message}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
    
    agent = create_openai_tools_agent(llm, tools, prompt)
    
    return AgentExecutor(agent=agent, tools=tools, verbose=True, return_intermediate_steps=True)

async def client_confirmation_node(state: OrchestratorState, agent: AgentExecutor) -> OrchestratorState:
    """
    Invoca al agente de confirmación y procesa su respuesta para actualizar el estado.
    """
    logger.debug("---WORKER: Agente de Confirmación y Procesamiento de Cliente---")

    message = state.get("message", "")

    confirmation_request = state.get("confirmation_request")
    if not confirmation_request:
        return {"next_node": NextNode.COLLECT_CLIENT_DATA}

    try:
        confirmation_data_str = "\n".join([f"- {k}: {v}" for k, v in confirmation_request.items()])
        response = await agent.ainvoke({
            "message": message,
            "confirmation_data": confirmation_data_str
        })
        
        output = response.get("output", "")
        intermediate_steps = response.get("intermediate_steps", [])

        state_update: OrchestratorState = {"confirmation_request": None}

        if intermediate_steps:
            logger.debug("---WORKER: Herramientas ejecutadas. Actualizando estado.---")
            for step in intermediate_steps:
                tool_output = step[1]
                if isinstance(tool_output, ClientResult):
                    state_update["client"] = tool_output
            state_update["base_message"] = [output or "Tus datos han sido registrados."]
        else:
            try:
                parsed_response = AgentResponse.parse_raw(output)
                state_update["base_message"] = [parsed_response.base_message]
                if parsed_response.clear_data:
                    logger.warning("---WORKER: Usuario negó los datos. Limpiando campos.---")
                    fields_to_clear = list(confirmation_request.keys())
                    for field in fields_to_clear:
                        state_update[field] = None
            except Exception:
                 state_update["base_message"] = [output]

        return state_update

    except Exception as e:
        logger.error(f"Ocurrió un error en el agente de confirmación: {e}", exc_info=True)
        return {"base_message": ["Hubo un problema procesando tu respuesta. Por favor, intenta de nuevo."]}