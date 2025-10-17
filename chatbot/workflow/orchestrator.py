from functools import partial
from typing import Literal
from logger import logger
from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.state import CompiledStateGraph
from langgraph.graph import StateGraph, END

from workflow.orchestrator_state import NextNode, OrchestratorState
from workflow.workers.response_generator_worker import create_response_generator_agent, response_generator_node
from workflow.workers.supervisor_worker import create_supervisor_agent, supervisor_node
from workflow.workers.client_validator_worker import create_client_validator_agent, client_validator_node
from workflow.workers.client_confirmation_worker import create_client_confirmation_agent, client_confirmation_node
from workflow.workers.vehicle_validator_worker import create_vehicle_validator_agent, vehicle_validator_node
from workflow.workers.vehicle_confirmation_worker import create_vehicle_confirmation_agent, vehicle_confirmation_node
from workflow.workers.eligibility_worker import create_eligibility_agent, eligibility_check_node


# --- Nodos Placeholder para ilustrar el flujo ---
def query_vehicles_node(state: OrchestratorState) -> dict:
    print("---WORKER: Consultando Vehículos---")
    return {"next_node": NextNode.GENERATE_RESPONSE}

def fallback_node(state: OrchestratorState) -> dict:
    print("---FALLBACK---")
    return {"next_node": NextNode.GENERATE_RESPONSE}

# --- Enrutador ---
def supervisor_router(state: OrchestratorState) -> Literal[
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
        ]:
    next_node = state.get('next_node', NextNode.FALLBACK)
    logger.info(f"---ROUTER: Decisión -> {next_node}---")
    return next_node
    
def create_orchestrator(
        llm: BaseChatModel,
        memory: MemorySaver,
        ) -> CompiledStateGraph:
    """Crea y compila el grafo orquestador principal."""
    
    supervisor_agent = create_supervisor_agent(llm)
    response_generator_agent = create_response_generator_agent(llm)
    client_validator_agent = create_client_validator_agent(llm)
    client_processor_agent = create_client_confirmation_agent(llm)
    vehicle_validator_agent = create_vehicle_validator_agent(llm)
    vehicle_confirmation_agent = create_vehicle_confirmation_agent(llm)
    eligibility_agent = create_eligibility_agent(llm)

    supervisor_node_partial = partial(supervisor_node, agent=supervisor_agent)
    response_generator_node_partial = partial(
        response_generator_node, agent=response_generator_agent
    )
    client_validator_node_partial = partial(
        client_validator_node, agent=client_validator_agent
    )   
    client_confirmation_node_partial = partial(
        client_confirmation_node, agent=client_processor_agent
    )
    vehicle_validator_node_partial = partial(
        vehicle_validator_node, agent=vehicle_validator_agent
    )
    vehicle_confirmation_node_partial = partial(
        vehicle_confirmation_node, agent=vehicle_confirmation_agent
    )
    eligibility_check_node_partial = partial(
        eligibility_check_node, agent=eligibility_agent
    )

    workflow = StateGraph(OrchestratorState)
    
    workflow.add_node("supervisor", supervisor_node_partial)
    workflow.add_node(NextNode.COLLECT_CLIENT_DATA, client_validator_node_partial)
    workflow.add_node(NextNode.CONFIRM_CLIENT_DATA, client_confirmation_node_partial)
    workflow.add_node(NextNode.COLLECT_VEHICLE_DATA, vehicle_validator_node_partial)
    workflow.add_node(NextNode.CONFIRM_VEHICLE_DATA, vehicle_confirmation_node_partial)
    workflow.add_node(NextNode.CHECK_ELIGIBILITY, eligibility_check_node_partial)
    workflow.add_node(NextNode.FALLBACK, fallback_node)
    workflow.add_node(NextNode.GENERATE_RESPONSE, response_generator_node_partial)

    workflow.set_entry_point("supervisor")

    workflow.add_conditional_edges(
        "supervisor",
        supervisor_router,
        {
            NextNode.COLLECT_CLIENT_DATA: NextNode.COLLECT_CLIENT_DATA,
            NextNode.CONFIRM_CLIENT_DATA: NextNode.CONFIRM_CLIENT_DATA,
            NextNode.COLLECT_VEHICLE_DATA: NextNode.COLLECT_VEHICLE_DATA,
            NextNode.CONFIRM_VEHICLE_DATA: NextNode.CONFIRM_VEHICLE_DATA,
            NextNode.CHECK_ELIGIBILITY: NextNode.CHECK_ELIGIBILITY,
            NextNode.GENERATE_RESPONSE: NextNode.GENERATE_RESPONSE,
            NextNode.FALLBACK: NextNode.FALLBACK,
        },
    )
    
    # Definición de las transiciones entre nodos
    workflow.add_edge(NextNode.COLLECT_CLIENT_DATA, NextNode.GENERATE_RESPONSE)
    workflow.add_edge(NextNode.CONFIRM_CLIENT_DATA, NextNode.GENERATE_RESPONSE) 
    workflow.add_edge(NextNode.COLLECT_VEHICLE_DATA, NextNode.GENERATE_RESPONSE)
    workflow.add_edge(NextNode.CONFIRM_VEHICLE_DATA, NextNode.GENERATE_RESPONSE)
    workflow.add_edge(NextNode.CHECK_ELIGIBILITY, NextNode.GENERATE_RESPONSE)
    workflow.add_edge(NextNode.FALLBACK, NextNode.GENERATE_RESPONSE)    
    workflow.add_edge(NextNode.GENERATE_RESPONSE, END)
    
    compiled = workflow.compile(checkpointer=memory)
    return compiled