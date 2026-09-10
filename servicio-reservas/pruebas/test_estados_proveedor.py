"""Pruebas del endpoint interno de provider states."""

import pytest
from fastapi.testclient import TestClient

from aplicacion import almacen
from aplicacion.principal import app

cliente = TestClient(app)

# Los nombres de los estados quedan en inglés: son parte del contrato y
# deben escribirse igual en el consumidor y en el proveedor.
ESTADOS = [
    "a new valid reservation can be created",
    "a new invalid reservation can be rejected",
    "user U100 has an active reservation",
    "user U200 has no reservations",
    "reservation R-1001 exists and is active",
    "reservation R-9999 does not exist",
]

SOLICITUD_VALIDA = {
    "userId": "U100",
    "room": "SALA-1",
    "date": "2026-09-10",
    "hours": 2,
}


@pytest.fixture(autouse=True)
def almacen_limpio():
    almacen.limpiar()
    yield
    almacen.limpiar()


@pytest.fixture
def modo_pruebas(monkeypatch):
    """Activa PACT_TEST_MODE durante la prueba."""
    monkeypatch.setenv("PACT_TEST_MODE", "true")


def test_el_endpoint_esta_oculto_sin_modo_pruebas(monkeypatch):
    monkeypatch.delenv("PACT_TEST_MODE", raising=False)

    respuesta = cliente.post(
        "/_pact/provider-state", json={"state": ESTADOS[0], "action": "setup"}
    )

    assert respuesta.status_code == 404


@pytest.mark.parametrize("estado", ESTADOS)
def test_todos_los_estados_acordados_se_pueden_preparar(estado, modo_pruebas):
    respuesta = cliente.post(
        "/_pact/provider-state", json={"state": estado, "action": "setup"}
    )

    assert respuesta.status_code == 200


def test_un_estado_desconocido_se_rechaza(modo_pruebas):
    respuesta = cliente.post(
        "/_pact/provider-state", json={"state": "otro estado", "action": "setup"}
    )

    assert respuesta.status_code == 400
    assert respuesta.json()["error"] == "UNKNOWN_PROVIDER_STATE"


def test_estado_u100_tiene_una_reserva_activa(modo_pruebas):
    cliente.post(
        "/_pact/provider-state",
        json={"state": "user U100 has an active reservation", "action": "setup"},
    )

    respuesta = cliente.get("/users/U100/reservations")

    assert respuesta.status_code == 200
    assert respuesta.json() == [
        {
            "id": "R-1001",
            "userId": "U100",
            "room": "SALA-1",
            "date": "2026-09-10",
            "hours": 2,
            "active": True,
        }
    ]


def test_estado_u200_no_tiene_reservas(modo_pruebas):
    cliente.post("/reservations", json={
        "userId": "U200", "room": "SALA-2", "date": "2026-09-10", "hours": 1,
    })

    cliente.post(
        "/_pact/provider-state",
        json={"state": "user U200 has no reservations", "action": "setup"},
    )

    assert cliente.get("/users/U200/reservations").json() == []


def test_estado_r1001_existe_y_esta_activa(modo_pruebas):
    cliente.post(
        "/_pact/provider-state",
        json={"state": "reservation R-1001 exists and is active", "action": "setup"},
    )

    respuesta = cliente.get("/reservations/R-1001")

    assert respuesta.status_code == 200
    assert respuesta.json()["active"] is True


def test_estado_r9999_no_existe(modo_pruebas):
    cliente.post(
        "/_pact/provider-state",
        json={"state": "reservation R-9999 does not exist", "action": "setup"},
    )

    respuesta = cliente.get("/reservations/R-9999")

    assert respuesta.status_code == 404


def test_el_teardown_vacia_el_almacenamiento(modo_pruebas):
    cliente.post("/reservations", json=SOLICITUD_VALIDA)

    cliente.post(
        "/_pact/provider-state",
        json={"state": ESTADOS[0], "action": "teardown"},
    )

    assert cliente.get("/users/U100/reservations").json() == []
