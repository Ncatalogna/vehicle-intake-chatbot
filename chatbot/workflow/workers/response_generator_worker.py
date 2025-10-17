from typing import Any, Dict, List
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langchain_core.runnables import RunnableSerializable

from workflow.orchestrator_state import OrchestratorState
from logger import logger

def create_response_generator_agent(
    llm: BaseChatModel,
) -> RunnableSerializable[Dict[str, Any], BaseMessage]:
    """
    Crea un agente que genera respuestas para el usuario.
    """
    system_prompt_template = (
        "Eres un asistente virtual de 'Vehicle Intake'. Tu rol es guiar al usuario para recolectar información de manera amable y clara.\n\n"
        "**TAREA PRINCIPAL**\n"
        "Tu única tarea es convertir la 'INSTRUCCIÓN INTERNA' en una respuesta directa para el usuario, sin agregar otra cosa.\n"    
        "En caso que 'INSTRUCCIÓN INTERNA' este vacio o sin contexto, responder de forma amigable y formal.\n"
        "'INSTRUCCIÓN INTERNA' son intenciones nuevas y requerimientos apuntados al usuario (NO ES PARA TI), no estan relacionado a la respuesta del usuario.\n"
        "Solo responde con un saludo amigable y informando quien sos, si 'INSTRUCCIÓN INTERNA' lo solicita. Si no es el caso, responder directamente al punto.\n\n"
        "'CONTEXTO DEL CLIENTE' es quien determina con quien estas hablando, su nombre.\n"
        "Si 'CONTEXTO DEL CLIENTE' es 'ninguno, no asumas quien es el cliente.\n"        
        "```\n"
        "**INSTRUCCIÓN INTERNA**\n"
        "{base_message}\n"
        "```\n"
        "```\n"
        "**CONTEXTO DEL CLIENTE**\n"
        "{name_client_data}\n"
        "```\n"
        "**COMO RESPONDER**\n"
        "Recuerda que con todo el contexto anterior, tendras que responder de forma amigable y formal, siempre priorizando 'INSTRUCCIÓN INTERNA'.\n"
        "No validar mensaje del usuario con respecto a 'INSTRUCCIÓN INTERNA'."
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt_template),            
            MessagesPlaceholder(variable_name="message"),
        ]
    )

    agent = prompt | llm
    return agent

def response_generator_node(
    state: OrchestratorState,
    agent: RunnableSerializable[Dict[str, Any], BaseMessage],
) -> dict:
    """
    Ejecuta el agente generador de respuestas y actualiza el estado.
    """
    logger.debug("---WORKER: Generando Respuesta Final (con Contexto)---")
    
    base_message = state.get("base_message", [])
    message = state.get("message", "")

    instruccion_interna_str = '\n'.join([f"- {valor}" for valor in base_message]) if base_message else "ninguno"
    logger.debug(f"---WORKER: Instrucción Interna -> {instruccion_interna_str}---")

    client = state.get("client")
    name = client.name if client and client.name and client.id else None
    
    name_client_data = (
        f"- El nombre del cliente es: {name}" if name else "ninguno"
    )

    response = agent.invoke({
        "message": message,
        "name_client_data": name_client_data,
        "base_message": instruccion_interna_str
    })
    
    return {"messages": [response]}