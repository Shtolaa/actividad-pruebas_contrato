"""Servicio de Reservas (proveedor Pact).

Expone los tres endpoints acordados con los consumidores.

Las rutas, los códigos de estado, los nombres de los campos y los nombres
de los provider states están fijados por el contrato y por eso quedan en
inglés; todo lo demás está en español.
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from aplicacion import almacen
from aplicacion.modelos import Reserva, SolicitudReserva

app = FastAPI(title="Servicio de Reservas")


@app.post("/reservations", status_code=201)
def crear_reserva(solicitud: SolicitudReserva) -> JSONResponse:
    """Crea una reserva. La rechaza con 400 si hours <= 0."""
    if solicitud.hours <= 0:
        return JSONResponse(status_code=400, content={"error": "INVALID_HOURS"})

    reserva = Reserva(
        id=almacen.siguiente_id(),
        userId=solicitud.userId,
        room=solicitud.room,
        date=solicitud.date,
        hours=solicitud.hours,
        active=True,
    )
    almacen.guardar(reserva)
    return JSONResponse(status_code=201, content=reserva.model_dump())


@app.get("/users/{usuario_id}/reservations")
def reservas_del_usuario(usuario_id: str) -> JSONResponse:
    """Devuelve las reservas del usuario. La lista vacía es válida."""
    reservas = [reserva.model_dump() for reserva in almacen.buscar_por_usuario(usuario_id)]
    return JSONResponse(status_code=200, content=reservas)


@app.get("/reservations/{reserva_id}")
def obtener_reserva(reserva_id: str) -> JSONResponse:
    """Devuelve la reserva pedida, o 404 si no existe."""
    reserva = almacen.buscar_por_id(reserva_id)
    if reserva is None:
        return JSONResponse(
            status_code=404, content={"error": "RESERVATION_NOT_FOUND"}
        )
    return JSONResponse(status_code=200, content=reserva.model_dump())

