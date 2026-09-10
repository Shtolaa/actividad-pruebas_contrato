"""Verifica el Servicio de Reservas contra todos los Pact generados."""

import os
from pathlib import Path
from urllib.parse import urlsplit

from pact import Verifier


ROOT_DIR = Path(__file__).resolve().parents[1]
PACT_DIR = ROOT_DIR / "pacts"
PROVIDER_URL = os.getenv("PROVIDER_URL", "http://localhost:8000").rstrip("/")
PROVIDER_HOST = urlsplit(PROVIDER_URL).hostname or "localhost"


def test_reservation_service_honors_consumer_contracts() -> None:
    """Reproduce las seis interacciones contra el proveedor real."""
    verifier = (
        Verifier("Reservation Service", host=PROVIDER_HOST)
        .add_source(str(PACT_DIR))
        .add_transport(url=PROVIDER_URL)
        .state_handler(
            f"{PROVIDER_URL}/_pact/provider-state",
            teardown=True,
            body=True,
        )
    )

    verifier.verify()
