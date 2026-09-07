# Servicio de Reservas

Proveedor Pact del sistema. Es el único servicio que guarda reservas: los otros
dos microservicios (Portal de Usuario y Servicio de Administración) y la
Aplicación de Reserva lo consumen por HTTP/JSON.

- Lenguaje: Python + FastAPI (Uvicorn)
- Puerto: `8000`
- Persistencia: **en memoria** (diccionario). No hay base de datos: al reiniciar
  el proceso se pierden las reservas.

## Estructura

```text
servicio-reservas/
├── aplicacion/
│   ├── principal.py   # endpoints + endpoint interno de provider states
│   ├── modelos.py     # SolicitudReserva y Reserva
│   └── almacen.py     # almacenamiento en memoria
├── pruebas/           # pruebas esenciales (pytest)
├── requisitos.txt
└── Dockerfile
```

## Qué está en español y qué no

El código, los comentarios y la documentación están en español. Se mantienen en
inglés, porque son **el contrato acordado** con los consumidores y cambiarlos
rompería los Pact:

- las rutas: `/reservations`, `/users/{userId}/reservations`, `/reservations/{id}`;
- los nombres de los campos JSON: `id`, `userId`, `room`, `date`, `hours`, `active`;
- los códigos de error: `INVALID_HOURS`, `RESERVATION_NOT_FOUND`;
- los seis nombres de provider state;
- la variable de entorno `PACT_TEST_MODE`.

## Modelo de datos

```json
{
  "id": "R-1001",
  "userId": "U100",
  "room": "SALA-1",
  "date": "2026-09-10",
  "hours": 2,
  "active": true
}
```

El `id` se genera dinámicamente con el formato `R-1001`, `R-1002`, ..., por eso
los consumidores deben usar un matcher Pact para ese campo.

## Endpoints

### `POST /reservations`

Crea una reserva.

```json
{ "userId": "U100", "room": "SALA-1", "date": "2026-09-10", "hours": 2 }
```

- `201 Created` con la reserva creada (`active = true`).
- `400 Bad Request` con `{"error": "INVALID_HOURS"}` si `hours <= 0`.

### `GET /users/{userId}/reservations`

Devuelve las reservas de un usuario.

- `200 OK` con la lista de reservas.
- `200 OK` con `[]` si el usuario no tiene reservas (respuesta válida, no es un error).

### `GET /reservations/{reservationId}`

Devuelve una reserva concreta.

- `200 OK` con la reserva.
- `404 Not Found` con `{"error": "RESERVATION_NOT_FOUND"}` si no existe.

El Servicio de Administración interpreta `200 + active=true` como reserva válida
y `404` como reserva no válida.

## Provider states

Para la verificación del proveedor existe un endpoint **solo de pruebas**:

```http
POST /_pact/provider-state
```

```json
{ "state": "user U100 has an active reservation", "action": "setup" }
```

Se habilita únicamente con la variable de entorno:

```text
PACT_TEST_MODE=true
```

Si la variable no vale `true`, el endpoint responde `404` y no puede usarse.

Estados acordados (los nombres deben escribirse exactamente así):

| Provider state | Preparación |
|---|---|
| `a new valid reservation can be created` | vacía el almacenamiento |
| `a new invalid reservation can be rejected` | vacía el almacenamiento |
| `user U100 has an active reservation` | vacía y crea `R-1001` de `U100` |
| `user U200 has no reservations` | elimina las reservas de `U200` |
| `reservation R-1001 exists and is active` | vacía y crea `R-1001` activa |
| `reservation R-9999 does not exist` | elimina `R-9999` si existiera |

Respuestas del endpoint:

- `200 OK` si el estado se preparó (también para `"action": "teardown"`, que vacía todo).
- `400 Bad Request` con `{"error": "UNKNOWN_PROVIDER_STATE"}` si el nombre no es uno de los seis.
- `404 Not Found` si `PACT_TEST_MODE` no está activo.

## Ejecutar en local

```bash
cd servicio-reservas
python3 -m venv .venv
source .venv/bin/activate
pip install -r requisitos.txt
PACT_TEST_MODE=true uvicorn aplicacion.principal:app --host 0.0.0.0 --port 8000
```

## Ejecutar las pruebas

```bash
cd servicio-reservas
.venv/bin/python -m pytest -q
```

## Docker

```bash
docker build -t servicio-reservas ./servicio-reservas
docker run -p 8000:8000 -e PACT_TEST_MODE=true servicio-reservas
```

## Datos de integración (para la Persona 5)

```text
Carpeta para docker compose:  ./servicio-reservas
URL en local:                 http://localhost:8000
Puerto:                       8000
Provider states:              POST /_pact/provider-state
Variable requerida:           PACT_TEST_MODE=true
```

La URL que usan el Portal de Usuario y el Servicio de Administración dentro de
Docker (`RESERVATION_SERVICE_URL`) depende del nombre que reciba el servicio en
`docker-compose.yml`; si se llama `servicio-reservas`, la URL es
`http://servicio-reservas:8000`.
