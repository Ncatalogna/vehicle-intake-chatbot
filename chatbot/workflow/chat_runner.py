from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.state import CompiledStateGraph
from langchain_core.runnables import RunnableConfig
from langchain.globals import set_debug
from workflow.orchestrator import create_orchestrator


class ChatRunner:
    """
    Encapsulates the chat workflow, managing the language model, memory, and session.
    """

    def __init__(
        self,
        llm: BaseChatModel,
        memory: MemorySaver,
        session_id: str,
    ):
        self.llm = llm
        self.memory = memory
        self.session_id = session_id
        # Inicializar tu grafo de LangGraph
        self.graph: CompiledStateGraph = create_orchestrator(self.llm, self.memory)

    async def handle_message(self, message: str):
        """Handles an incoming message and returns the bot's response."""
        config: RunnableConfig = {"configurable": {"thread_id": self.session_id}}
        set_debug(False)
        
        initial_input = {
            "message": [("user", message)],
        }
        
        response = await self.graph.ainvoke(initial_input, config)
        return response["messages"][-1].content