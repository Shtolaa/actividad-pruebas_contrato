"""Servicio de Reservas (proveedor Pact).

Expone los tres endpoints acordados con los consumidores y, solo en modo
de pruebas, un endpoint interno para preparar los provider states.

Las rutas, los códigos de estado, los nombres de los campos y los nombres
de los provider states están fijados por el contrato y por eso quedan en
inglés; todo lo demás está en español.
"""

import os

from fastapi import FastAPI, Request
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


# --- Solo para las pruebas de contrato ---------------------------------------

RESERVA_R1001 = Reserva(
    id="R-1001",
    userId="U100",
    room="SALA-1",
    date="2026-09-10",
    hours=2,
    active=True,
)


def _modo_pruebas_activo() -> bool:
    """Indica si PACT_TEST_MODE habilita el endpoint de provider states."""
    return os.getenv("PACT_TEST_MODE", "").lower() == "true"


def _preparar_estado(estado: str) -> bool:
    """Prepara el almacenamiento para el provider state pedido.

    Devuelve False si el nombre del estado no es uno de los seis acordados.
    """
    if estado == "a new valid reservation can be created":
        almacen.limpiar()
    elif estado == "a new invalid reservation can be rejected":
        almacen.limpiar()
    elif estado == "user U100 has an active reservation":
        almacen.limpiar()
        almacen.guardar(RESERVA_R1001)
    elif estado == "user U200 has no reservations":
        for reserva in almacen.buscar_por_usuario("U200"):
            almacen.eliminar(reserva.id)
    elif estado == "reservation R-1001 exists and is active":
        almacen.limpiar()
        almacen.guardar(RESERVA_R1001)
    elif estado == "reservation R-9999 does not exist":
        almacen.eliminar("R-9999")
    else:
        return False
    return True


@app.post("/_pact/provider-state")
async def estado_del_proveedor(peticion: Request) -> JSONResponse:
    """Prepara los datos de un provider state durante la verificación Pact.

    Solo responde cuando PACT_TEST_MODE=true; en cualquier otro caso el
    endpoint no existe para el mundo exterior.
    """
    if not _modo_pruebas_activo():
        return JSONResponse(status_code=404, content={"error": "NOT_FOUND"})

    cuerpo = await peticion.json()
    estado = cuerpo.get("state", "")
    accion = cuerpo.get("action", "setup")

    if accion == "teardown":
        almacen.limpiar()
        return JSONResponse(status_code=200, content={"state": estado, "action": accion})

    if not _preparar_estado(estado):
        return JSONResponse(
            status_code=400,
            content={"error": "UNKNOWN_PROVIDER_STATE", "state": estado},
        )

    return JSONResponse(status_code=200, content={"state": estado, "action": accion})
