import os
import httpx

class BaseApiClient:
    """
    Cliente base de API que maneja la configuración de la URL y el cliente HTTP.
    """
    def __init__(self):
        self.base_url = os.getenv("API_URL", "http://localhost:8000")

    def get_api_client(self) -> httpx.AsyncClient:
        """Retorna una instancia del cliente HTTP asíncrono."""
        return httpx.AsyncClient(base_url=self.base_url)