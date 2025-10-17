import datetime
import uuid
from typing import Optional, List
from langchain_core.tools import tool, BaseTool
from typing import Annotated

from ..orchestrator_state import ClientResult, IdentificationType
from api.clients.client_client import ClientApiClient
from api.requests.client_request import ClientRequest, IdentificationType as RequestIdentificationType

api_client = ClientApiClient()

def client_tool() -> List[BaseTool]:

    @tool(description="Consulta un cliente por su número de documento. Retorna None si no existe.")
    async def query_client(
        documento: Annotated[str, "El número de documento del cliente."]
    ) -> Optional[ClientResult]:
        """Busca un cliente por su número de documento y retorna una instancia de ClientResult o None si no existe."""
        clients = await api_client.get_all_clients()
        for client in clients:
            if client.documento == documento:
                return ClientResult(**client.model_dump())
        return None

    @tool(description="Genera un nuevo cliente con todos sus datos.")
    async def insert_client(
        name: Annotated[str, "El nombre de pila del usuario."],
        last_name: Annotated[str, "El apellido del usuario."],
        birth_date: Annotated[datetime.date, "La fecha de nacimiento del usuario en formato YYYY-MM-DD."],
        documento: Annotated[str, "El número de documento del usuario."],
        documento_type: Annotated[IdentificationType, "El tipo de documento (DNI, CUIT o CUIL)."],
        email: Annotated[str, "El correo electrónico del usuario."],
        phone_number: Annotated[str, "El número de teléfono del usuario."]
    ) -> ClientResult:
        """Genera internamente un cliente y lo guarda en la base de datos en memoria."""
        client_data = ClientRequest(
            name=name,
            last_name=last_name,
            birth_date=birth_date,
            documento=documento,
            documento_type=RequestIdentificationType(documento_type.value),
            email=email,
            phone_number=phone_number
        )
        created_client = await api_client.create_client(client_data)
        return ClientResult(**created_client.model_dump())

    @tool(description="Actualiza los datos de un cliente existente.")
    async def update_client(
        client_id: Annotated[uuid.UUID, "El ID del cliente a actualizar."],
        name: Annotated[Optional[str], "El nombre de pila del usuario."] = None,
        last_name: Annotated[Optional[str], "El apellido del usuario."] = None,
        birth_date: Annotated[Optional[datetime.date], "La fecha de nacimiento del usuario en formato YYYY-MM-DD."] = None,
        documento: Annotated[Optional[str], "El número de documento del usuario."] = None,
        documento_type: Annotated[Optional[IdentificationType], "El tipo de documento (DNI, CUIT o CUIL)."] = None,
        email: Annotated[Optional[str], "El correo electrónico del usuario."] = None,
        phone_number: Annotated[Optional[str], "El número de teléfono del usuario."] = None
    ) -> ClientResult:
        """Actualiza internamente los datos de un cliente."""
        client_to_update = await api_client.get_client(client_id)
        if not client_to_update:
            raise ValueError(f"No se encontró un cliente con el ID {client_id}")

        update_data = client_to_update.model_dump()
        if name:
            update_data['name'] = name
        if last_name:
            update_data['last_name'] = last_name
        if birth_date:
            update_data['birth_date'] = birth_date
        if documento:
            update_data['documento'] = documento
        if documento_type:
            update_data['documento_type'] = RequestIdentificationType(documento_type.value)
        if email:
            update_data['email'] = email
        if phone_number:
            update_data['phone_number'] = phone_number
        
        client_request = ClientRequest(**update_data)
        updated_client = await api_client.update_client(client_id, client_request)
        if not updated_client:
            raise ValueError(f"No se pudo actualizar el cliente con el ID {client_id}")
        return ClientResult(**updated_client.model_dump())

    return [query_client, insert_client, update_client]