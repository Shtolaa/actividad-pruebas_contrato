# Portal de Usuario

Microservicio consumidor del Servicio de Reservas. Solo hace una cosa: recibe la
consulta de las reservas de un usuario, se la pide al Servicio de Reservas y
devuelve el resultado. No guarda nada ni tiene login, perfiles ni frontend.

- Lenguaje: Node.js + Express
- Puerto: `3000`
- Cliente HTTP: `fetch` nativo de Node
- Pact: `@pact-foundation/pact` (consumer `User Portal`, provider `Reservation Service`)

## Estructura

```text
user-portal/
├── src/
│   ├── app.js                # servidor Express y su único endpoint
│   └── reservationClient.js  # cliente hacia el Servicio de Reservas
├── tests/
│   └── reservations.pact.test.js
├── package.json
└── Dockerfile
```

## Endpoint

### `GET /portal/users/{userId}/reservations`

Llama a `GET /users/{userId}/reservations` del Servicio de Reservas y devuelve
tal cual su respuesta.

- `200 OK` con la lista de reservas del usuario.
- `200 OK` con `[]` si el usuario no tiene reservas (respuesta válida, no es un error).

## Configuración

| Variable | Valor por defecto | Descripción |
|---|---|---|
| `RESERVATION_SERVICE_URL` | `http://localhost:8000` | URL base del Servicio de Reservas |

## Ejecutar en local

```bash
cd user-portal
npm install
RESERVATION_SERVICE_URL=http://localhost:8000 npm start
```

En Windows PowerShell:

```powershell
$env:RESERVATION_SERVICE_URL = "http://localhost:8000"
npm start
```

```bash
curl http://localhost:3000/portal/users/U100/reservations
```

## Ejecutar las pruebas Pact

```bash
cd user-portal
npm install
npm test
```

Las pruebas se ejecutan contra el **Pact Mock Server**, no contra el Servicio de
Reservas real, y escriben el contrato en `../pacts/User Portal-Reservation Service.json`.

Interacciones del contrato:

| Provider state | Petición | Respuesta esperada |
|---|---|---|
| `user U100 has an active reservation` | `GET /users/U100/reservations` | `200` con al menos la reserva `R-1001` de `U100` y `active = true` |
| `user U200 has no reservations` | `GET /users/U200/reservations` | `200` con `[]` |

## Docker

```bash
docker build -t user-portal ./user-portal
docker run -p 3000:3000 -e RESERVATION_SERVICE_URL=http://localhost:8000 user-portal
```

## Datos de integración (para la Persona 5)

```text
Carpeta para docker compose:  ./user-portal
Puerto:                       3000
Variable requerida:           RESERVATION_SERVICE_URL
Comando de pruebas Pact:      cd user-portal && npm install && npm test
Contrato generado:            pacts/User Portal-Reservation Service.json
```

Dentro del `docker-compose.yml` de este repositorio, el Servicio de Reservas se
llama `reservation-service`, por lo que la URL es
`http://reservation-service:8000`.
