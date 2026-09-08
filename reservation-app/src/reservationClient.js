async function createReservation(baseUrl, userId, room, date, hours) {
  const response = await fetch(`${baseUrl}/reservations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ userId, room, date, hours })
  });

  return {
    status: response.status,
    body: await response.json()
  };
}

export { createReservation };
