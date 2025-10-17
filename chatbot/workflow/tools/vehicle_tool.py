import uuid
from typing import Optional, List
from langchain_core.tools import tool, BaseTool
from typing import Annotated

from ..orchestrator_state import VehicleResult
from api.clients.vehicle_client import VehicleApiClient
from api.requests.vehicle_request import VehicleRequest

api_client = VehicleApiClient()

def vehicle_tool() -> List[BaseTool]:

    @tool(description="Consulta un vehículo por su patente. Retorna None si no existe.")
    async def query_vehicle(
        license_plate: Annotated[str, "La patente del vehículo."],
        client_id: Annotated[uuid.UUID, "El ID del cliente al que pertenece el vehículo."]
    ) -> Optional[VehicleResult]:
        """Busca un vehículo por su patente y retorna una instancia de VehicleResult o None si no existe."""
        vehicles = await api_client.get_client_vehicles(client_id)
        for vehicle in vehicles:
            if vehicle.license_plate == license_plate:
                return VehicleResult(**vehicle.model_dump())
        return None

    @tool(description="Genera un nuevo vehículo con todos sus datos.")
    async def insert_vehicle(
        license_plate: Annotated[str, "La patente del vehículo."],
        brand: Annotated[str, "La marca del vehículo."],
        model: Annotated[str, "El modelo del vehículo."],
        year: Annotated[int, "El año de fabricación del vehículo."],
        mileage: Annotated[int, "El kilometraje del vehículo."],
        client_id: Annotated[uuid.UUID, "El ID del cliente al que se asociará el vehículo."]
    ) -> VehicleResult:
        """Genera internamente un vehículo y lo guarda en la base de datos a través de la API."""
        vehicle_data = VehicleRequest(
            client_id=client_id,
            license_plate=license_plate,
            brand=brand,
            model=model,
            year=year,
            mileage=mileage
        )
        created_vehicle = await api_client.create_vehicle(vehicle_data)
        return VehicleResult(**created_vehicle.model_dump())

    @tool(description="Actualiza los datos de un vehículo existente.")
    async def update_vehicle(
        vehicle_id: Annotated[uuid.UUID, "El ID del vehículo a actualizar."],
        client_id: Annotated[uuid.UUID, "El ID del cliente propietario del vehículo."],
        license_plate: Annotated[Optional[str], "La patente del vehículo."] = None,
        brand: Annotated[Optional[str], "La marca del vehículo."] = None,
        model: Annotated[Optional[str], "El modelo del vehículo."] = None,
        year: Annotated[Optional[int], "El año de fabricación del vehículo."] = None,
        mileage: Annotated[Optional[int], "El kilometraje del vehículo."] = None
    ) -> VehicleResult:
        """Actualiza internamente los datos de un vehículo a través de la API."""
        vehicle_to_update = await api_client.get_vehicle(vehicle_id)
        if not vehicle_to_update:
            raise ValueError(f"No se encontró un vehículo con el ID {vehicle_id}")

        update_data = vehicle_to_update.model_dump()
        update_data['client_id'] = client_id

        if license_plate:
            update_data['license_plate'] = license_plate
        if brand:
            update_data['brand'] = brand
        if model:
            update_data['model'] = model
        if year:
            update_data['year'] = year
        if mileage:
            update_data['mileage'] = mileage
        
        vehicle_request = VehicleRequest(**update_data)
        updated_vehicle = await api_client.update_vehicle(vehicle_id, vehicle_request)
        if not updated_vehicle:
            raise ValueError(f"No se pudo actualizar el vehículo con el ID {vehicle_id}")
        return VehicleResult(**updated_vehicle.model_dump())

    return [query_vehicle, insert_vehicle, update_vehicle]