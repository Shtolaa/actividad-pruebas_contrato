"""Modelos de datos del Servicio de Reservas.

Los nombres de los campos NO se traducen: son el formato JSON acordado
con los consumidores (Aplicación de Reserva, Portal de Usuario y Servicio
de Administración). Cambiarlos rompería los contratos Pact.
"""

from pydantic import BaseModel


class SolicitudReserva(BaseModel):
    """Cuerpo esperado en POST /reservations."""

    userId: str
    room: str
    date: str
    hours: int


class Reserva(BaseModel):
    """Reserva tal como se devuelve en todas las respuestas."""

    id: str
    userId: str
    room: str
    date: str
    hours: int
    active: bool
