"""Pruebas esenciales del Servicio de Reservas."""

import pytest
from fastapi.testclient import TestClient

from aplicacion import almacen
from aplicacion.principal import app

cliente = TestClient(app)

SOLICITUD_VALIDA = {
    "userId": "U100",
    "room": "SALA-1",
    "date": "2026-09-10",
    "hours": 2,
}


@pytest.fixture(autouse=True)
def almacen_limpio():
    """Cada prueba arranca y termina con el almacenamiento vacío."""
    almacen.limpiar()
    yield
    almacen.limpiar()


def test_crear_reserva_valida_devuelve_201():
    respuesta = cliente.post("/reservations", json=SOLICITUD_VALIDA)

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["id"]
    assert cuerpo["userId"] == "U100"
    assert cuerpo["room"] == "SALA-1"
    assert cuerpo["date"] == "2026-09-10"
    assert cuerpo["hours"] == 2
    assert cuerpo["active"] is True


def test_crear_reserva_con_cero_horas_devuelve_400():
    respuesta = cliente.post("/reservations", json={**SOLICITUD_VALIDA, "hours": 0})

    assert respuesta.status_code == 400
    assert respuesta.json() == {"error": "INVALID_HOURS"}


def test_reservas_de_un_usuario_con_reservas():
    creada = cliente.post("/reservations", json=SOLICITUD_VALIDA).json()

    respuesta = cliente.get("/users/U100/reservations")

    assert respuesta.status_code == 200
    assert respuesta.json() == [creada]


def test_reservas_de_un_usuario_sin_reservas_devuelve_lista_vacia():
    respuesta = cliente.get("/users/U200/reservations")

    assert respuesta.status_code == 200
    assert respuesta.json() == []


def test_obtener_reserva_existente():
    creada = cliente.post("/reservations", json=SOLICITUD_VALIDA).json()

    respuesta = cliente.get(f"/reservations/{creada['id']}")

    assert respuesta.status_code == 200
    assert respuesta.json() == creada


def test_obtener_reserva_inexistente_devuelve_404():
    respuesta = cliente.get("/reservations/R-9999")

    assert respuesta.status_code == 404
    assert respuesta.json() == {"error": "RESERVATION_NOT_FOUND"}
