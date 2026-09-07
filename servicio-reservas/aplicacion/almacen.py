"""Almacenamiento en memoria de las reservas.

No hay base de datos: las reservas viven en un diccionario mientras el
proceso está vivo. Es suficiente para la actividad y hace que los provider
states de Pact sean triviales de reproducir.
"""

from aplicacion.modelos import Reserva

_reservas: dict[str, Reserva] = {}
_siguiente_numero = 1001


def limpiar() -> None:
    """Vacía el almacenamiento y reinicia el generador de identificadores."""
    global _siguiente_numero
    _reservas.clear()
    _siguiente_numero = 1001


def siguiente_id() -> str:
    """Devuelve un identificador nuevo con el formato R-1001, R-1002, ..."""
    global _siguiente_numero
    identificador = f"R-{_siguiente_numero}"
    _siguiente_numero += 1
    return identificador


def guardar(reserva: Reserva) -> Reserva:
    """Guarda (o reemplaza) una reserva."""
    _reservas[reserva.id] = reserva
    return reserva


def buscar_por_id(identificador: str) -> Reserva | None:
    """Devuelve la reserva con ese identificador, o None si no existe."""
    return _reservas.get(identificador)


def buscar_por_usuario(usuario_id: str) -> list[Reserva]:
    """Devuelve las reservas del usuario; lista vacía si no tiene ninguna."""
    return [reserva for reserva in _reservas.values() if reserva.userId == usuario_id]


def eliminar(identificador: str) -> None:
    """Elimina una reserva si existe; no falla si no existe."""
    _reservas.pop(identificador, None)
