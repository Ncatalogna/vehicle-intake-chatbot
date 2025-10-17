import os
from pydantic import SecretStr

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

def get_llm() -> BaseChatModel:
    """
    Inicializa y devuelve una instancia del modelo de lenguaje_
    seleccionado mediante variables de entorno.

    Esta función lee la variable de entorno LLM_PROVIDER para decidir_
    si usar 'groq' o 'gemini'
    y configura el cliente correspondiente con su respectiva API key.
    """
    llm_provider = os.getenv("LLM_PROVIDER", "groq").lower()
    
    if llm_provider == "gemini":
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise ValueError(
                "La variable de entorno GEMINI_API_KEY no está configurada. "
                "Por favor, asegúrate de que esté definida en tu archivo .env."
            )
        print("--- Usando Gemini ---")
        return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            google_api_key=gemini_api_key,
            temperature=0.1,
            convert_system_message_to_human=True
        )
        
    elif llm_provider == "groq":
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError(
                "La variable de entorno GROQ_API_KEY no está configurada. "
                "Por favor, asegúrate de que esté definida en tu archivo .env."
            )
        print("--- Usando Groq ---")
        return ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=SecretStr(groq_api_key),
            temperature=0.1,
        )
    
    else:
        raise ValueError(
            f"Proveedor de LLM no válido: '{llm_provider}'. "
            "Las opciones válidas son 'groq' o 'gemini'."
        )