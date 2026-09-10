# Pruebas de contrato en microservicios

Implementación de la actividad de pruebas de contrato con Pact para un sistema
de reservas de salas. El proveedor central es un servicio FastAPI y existen dos
microservicios consumidores: el Portal de Usuario y el Servicio de
Administración. La Aplicación de Reserva es solamente un cliente de prueba para
generar el primer contrato.

El flujo demostrado es:

```text
Consumidor -> Pact Mock Server -> contrato en ./pacts
                                      |
                                      v
                         Pact Verifier + provider states
                                      |
                                      v
                         Servicio de Reservas real
```

No se utiliza Pact Broker ni una base de datos.

## Estructura

```text
.
|-- servicio-reservas/       # Proveedor FastAPI, puerto 8000
|-- reservation-app/         # Consumidor Pact 1, sin servidor
|-- user-portal/             # Consumidor Express, puerto 3000
|-- administration-service/  # Consumidor Spring Boot, puerto 8080
|-- provider-verification/   # Verificación de los tres contratos
|-- pacts/                   # Contratos generados por las pruebas consumidoras
`-- docker-compose.yml       # Los tres microservicios
```

## Requisitos

- Docker Desktop con Docker Compose
- Node.js LTS y npm
- Python 3.10 o superior
- Java 21
- Maven 3.9 o superior

## Levantar los servicios

Desde la raíz del repositorio:

```bash
docker compose up -d --build
docker compose ps
```

Compose levanta únicamente estos servicios:

| Servicio | Puerto | Función |
|---|---:|---|
| `reservation-service` | 8000 | Proveedor de reservas |
| `user-portal` | 3000 | Consulta reservas por usuario |
| `administration-service` | 8080 | Valida una reserva |

El proveedor se inicia con `PACT_TEST_MODE=true`. Dentro de Docker, los
consumidores utilizan `http://reservation-service:8000` como URL del proveedor.

Para detenerlos:

```bash
docker compose down
```

## Ejecutar los contratos consumidores

Las siguientes pruebas utilizan un Pact Mock Server. No llaman al Servicio de
Reservas real.

### Contrato 1: Reservation App

Genera `Reservation App-Reservation Service.json` y verifica la creación válida
de una reserva y el rechazo de `hours=0`.

```bash
cd reservation-app
npm ci
npm test
cd ..
```

### Contrato 2: User Portal

Genera `User Portal-Reservation Service.json` y verifica la consulta de U100
con reservas y de U200 sin reservas.

```bash
cd user-portal
npm ci
npm test
cd ..
```

### Contrato 3: Administration Service

Genera `Administration Service-Reservation Service.json` y verifica R-1001
como reserva válida y R-9999 como reserva inexistente.

```bash
cd administration-service
mvn -Dtest=ReservationValidationPactTest test
cd ..
```

Los tres contratos se escriben automáticamente en `./pacts`. No deben
editarse manualmente.

## Verificar los contratos contra el proveedor

Primero deben estar levantados los servicios y generados los tres Pact.

Crear un entorno para el verificador e instalar sus dependencias:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r provider-verification/requirements.txt
```

En Windows PowerShell, si el entorno no está activado, se pueden usar
directamente estos comandos:

```powershell
.\.venv\Scripts\python.exe -m pip install -r provider-verification\requirements.txt
.\.venv\Scripts\python.exe -m pytest provider-verification\test_provider_pacts.py -s
```

En Linux o macOS:

```bash
.venv/bin/python -m pytest provider-verification/test_provider_pacts.py -s
```

El verificador:

1. carga los tres archivos Pact desde `./pacts`;
2. prepara el provider state mediante `POST /_pact/provider-state`;
3. reproduce cada interacción contra `http://localhost:8000`;
4. ejecuta el teardown del estado después de cada interacción.

El resultado esperado es `6 interactions verified` y cero fallos.

Para utilizar otra URL del proveedor:

```bash
PROVIDER_URL=http://127.0.0.1:8000 python -m pytest provider-verification/test_provider_pacts.py -s
```

En Windows PowerShell:

```powershell
$env:PROVIDER_URL = "http://127.0.0.1:8000"
.\.venv\Scripts\python.exe -m pytest provider-verification\test_provider_pacts.py -s
```

## Provider states

El Servicio de Reservas prepara los datos reproducibles solicitados por cada
contrato:

| Provider state | Datos preparados |
|---|---|
| `a new valid reservation can be created` | Almacenamiento vacío |
| `a new invalid reservation can be rejected` | Almacenamiento vacío |
| `user U100 has an active reservation` | Reserva activa `R-1001` de U100 |
| `user U200 has no reservations` | Sin reservas de U200 |
| `reservation R-1001 exists and is active` | Reserva activa `R-1001` |
| `reservation R-9999 does not exist` | R-9999 eliminada |

El endpoint de estados solo está habilitado cuando `PACT_TEST_MODE=true`.

## API del proveedor

| Método | Ruta | Resultado |
|---|---|---|
| `POST` | `/reservations` | `201` o `400` según `hours` |
| `GET` | `/users/{userId}/reservations` | `200` con lista, incluso vacía |
| `GET` | `/reservations/{reservationId}` | `200` o `404` |
| `POST` | `/_pact/provider-state` | Preparación de estados Pact |

## Pruebas del servicio de reservas

Las pruebas unitarias del proveedor pueden ejecutarse fuera de Docker:

```bash
cd servicio-reservas
python -m venv .venv
python -m pip install -r requisitos.txt
python -m pytest -q
cd ..
```

## Dificultades de integración

- La versión 16.5.0 de Pact JS no podía cargarse con Jest 30 y Node 22 por
  una dependencia ESM; los consumidores fijan `@pact-foundation/pact` en
  16.4.0, que mantiene las mismas APIs y permite ejecutar las pruebas.
- Los contratos Java y JavaScript usan versiones distintas de la especificación
  Pact, por lo que la verificación utiliza `pact-python` 3.x, compatible con
  Pact v3 y v4.
- Los provider states deben modificar el almacenamiento en memoria del proceso
  real, por eso se exponen mediante el endpoint interno habilitado por
  `PACT_TEST_MODE`.
- El Dockerfile original de Administración esperaba un JAR en `target/`, que
  está excluido por `.dockerignore`; se convirtió en una imagen multi-etapa para
  que Compose pueda construirla desde cero.

## Demostración sugerida

1. Ejecutar `docker compose up -d --build` y mostrar los tres servicios activos.
2. Ejecutar las pruebas de `reservation-app`, `user-portal` y
   `administration-service`.
3. Mostrar los tres archivos generados en `./pacts`.
4. Ejecutar la provider verification y mostrar las seis interacciones exitosas.
5. Explicar el flujo `consumer -> contract -> provider`.
