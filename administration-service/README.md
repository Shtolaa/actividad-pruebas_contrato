# Administration Service

Validates whether a reservation can be used by administrative workflows.

## Persona 5 handoff

- HTTP port: `8080`
- Run unit and consumer contract tests: `mvn test`
- Run Pact consumer tests: `mvn -Dtest=ReservationValidationPactTest test`
- Start with the reservation provider URL: `RESERVATION_SERVICE_URL=http://localhost:8000 mvn spring-boot:run`

En Windows PowerShell:

```powershell
$env:RESERVATION_SERVICE_URL = "http://localhost:8000"
mvn spring-boot:run
```

The Pact consumer tests generate `../pacts/Administration Service-Reservation Service.json`.
