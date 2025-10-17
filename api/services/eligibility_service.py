from uuid import UUID
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from .client_service import ClientService
from .vehicle_service import VehicleService
from responses.eligibility_response import EligibilityResponse

class EligibilityService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.client_service = ClientService(db_session)
        self.vehicle_service = VehicleService(db_session)

    async def check_eligibility(self, client_id: UUID, vehicle_id: UUID) -> EligibilityResponse:
        """
        Realiza la evaluación de elegibilidad para un cliente y su vehículo.

        Reglas:
        - Cliente debe ser mayor de 18 años.
        - El año del vehículo debe ser 2015 o más reciente.
        - El kilometraje del vehículo debe ser menor a 100,000 km.
        """
        client = await self.client_service.get_client_by_id(client_id)
        vehicle = await self.vehicle_service.get_vehicle_by_id(vehicle_id)

        if not client or not vehicle:
            return EligibilityResponse(
                is_eligible=False,
                message="No se pudo encontrar el cliente o el vehículo especificado.",
                reasons=["Cliente o vehículo no encontrado."]
            )

        reasons = []
        is_eligible = True

        # 1. Validación de Edad del Cliente (mayor de 18)
        if client.birth_date:
            today = date.today()
            age = today.year - client.birth_date.year - ((today.month, today.day) < (client.birth_date.month, client.birth_date.day))
            if age < 18:
                is_eligible = False
                reasons.append(f"El cliente es menor de 18 años (edad actual: {age}).")
        else:
            is_eligible = False
            reasons.append("La fecha de nacimiento del cliente no está registrada.")

        # 2. Validación del Año del Vehículo (posterior a 2015)
        if vehicle.year < 2015:
            is_eligible = False
            reasons.append(f"El vehículo es del año {vehicle.year} (debe ser de 2015 o más nuevo).")

        # 3. Validación del Kilometraje (menor a 100k)
        if vehicle.mileage >= 100000:
            is_eligible = False
            reasons.append(f"El vehículo tiene {vehicle.mileage} km (el límite es 100,000 km).")
        
        # Generar mensaje final
        if is_eligible:
            message = f"¡Felicidades, {client.name}! Eres elegible para el producto."
        else:
            message = f"Lo sentimos, {client.name}. No cumples con los criterios de elegibilidad."

        return EligibilityResponse(
            is_eligible=is_eligible,
            message=message,
            reasons=reasons
        )