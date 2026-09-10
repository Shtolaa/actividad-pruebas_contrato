// Cliente HTTP hacia el Servicio de Reservas.
// La URL del proveedor llega por la variable de entorno RESERVATION_SERVICE_URL.

async function getReservationsByUser(userId) {
  const baseUrl = process.env.RESERVATION_SERVICE_URL || 'http://localhost:8000';
  const response = await fetch(`${baseUrl}/users/${userId}/reservations`);

  return {
    status: response.status,
    body: await response.json()
  };
}

export { getReservationsByUser };
