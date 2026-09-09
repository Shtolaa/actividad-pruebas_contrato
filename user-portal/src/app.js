// Portal de Usuario: único endpoint, delega la consulta en el Servicio de Reservas.

import express from 'express';
import { getReservationsByUser } from './reservationClient.js';

const app = express();
const port = 3000;

app.get('/portal/users/:userId/reservations', async (req, res) => {
  const { status, body } = await getReservationsByUser(req.params.userId);
  res.status(status).json(body);
});

app.listen(port, () => {
  console.log(`Portal de Usuario escuchando en el puerto ${port}`);
});
