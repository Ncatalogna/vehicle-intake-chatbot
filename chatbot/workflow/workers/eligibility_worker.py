from typing import Dict, Any
from langchain_core.language_models import BaseChatModel
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from workflow.orchestrator_state import OrchestratorState, NextNode
from logger import logger
from workflow.tools.eligibility_tool import eligibility_tool, EligibilityResult

def create_eligibility_agent(llm: BaseChatModel) -> AgentExecutor:
    """
    Crea un agente cuya única función es ejecutar la herramienta de elegibilidad.
    """
    tools = eligibility_tool()

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system",
             "Tu única tarea es ejecutar la herramienta `check_eligibility` utilizando el ID de cliente y el ID de vehículo proporcionados en el contexto.\n"
             "No necesitas analizar el mensaje del usuario. La invocación de este worker es la señal para proceder.\n"
             "Contexto de la evaluación:\n"
             "- ID Cliente: {client_id}\n"
             "- ID Vehículo: {vehicle_id}"
            ),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
    
    agent = create_openai_tools_agent(llm, tools, prompt)
    
    return AgentExecutor(agent=agent, tools=tools, verbose=True, return_intermediate_steps=True)


async def eligibility_check_node(state: OrchestratorState, agent: AgentExecutor) -> dict:
    """
    Invoca al agente de elegibilidad y actualiza el estado con el resultado.
    """
    logger.debug("---WORKER: Evaluación de Elegibilidad---")

    client = state.get("client")
    vehicle = state.get("vehicle")

    if not client or not client.id or not vehicle or not vehicle.id:
        return {
            "base_message": ["No se encontraron los datos necesarios para la evaluación. Por favor, reinicia el proceso."],
            "next_node": NextNode.FALLBACK
        }

    try:
        response = await agent.ainvoke({
            "client_id": str(client.id),
            "vehicle_id": str(vehicle.id),
            "input": "Realizar evaluación de elegibilidad." # Input fijo, ya que no depende del usuario
        })
        
        output = response.get("output", "")
        intermediate_steps = response.get("intermediate_steps", [])

        state_update: Dict[str, Any] = {}

        if intermediate_steps:
            tool_output = intermediate_steps[0][1] # Solo esperamos un paso
            if isinstance(tool_output, EligibilityResult):
                logger.debug(f"---WORKER: Resultado de Elegibilidad -> {tool_output.checked_criteria} ---")
                state_update["base_message"] = [tool_output.message]
            else:
                 state_update["base_message"] = [str(tool_output)]
        else:
            state_update["base_message"] = [output or "No se pudo determinar la elegibilidad."]

        return state_update

    except Exception as e:
        logger.error(f"Ocurrió un error en el agente de elegibilidad: {e}", exc_info=True)
        return {"base_message": ["Hubo un problema al procesar la evaluación. Por favor, intenta de nuevo más tarde."]}