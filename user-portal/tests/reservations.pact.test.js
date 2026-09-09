import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { PactV3, MatchersV3 } from '@pact-foundation/pact';
import { getReservationsByUser } from '../src/reservationClient.js';

const { eachLike } = MatchersV3;
const __dirname = path.dirname(fileURLToPath(import.meta.url));

const provider = new PactV3({
  consumer: 'User Portal',
  provider: 'Reservation Service',
  dir: path.resolve(__dirname, '../../pacts')
});

describe('User Portal contract', () => {
  test('gets the reservations of a user that has one', async () => {
    provider
      .given('user U100 has an active reservation')
      .uponReceiving('a request for the reservations of U100')
      .withRequest({
        method: 'GET',
        path: '/users/U100/reservations'
      })
      .willRespondWith({
        status: 200,
        headers: { 'Content-Type': 'application/json' },
        body: eachLike({
          id: 'R-1001',
          userId: 'U100',
          room: 'SALA-1',
          date: '2026-09-10',
          hours: 2,
          active: true
        })
      });

    await provider.executeTest(async (mockServer) => {
      process.env.RESERVATION_SERVICE_URL = mockServer.url;

      const response = await getReservationsByUser('U100');

      expect(response.status).toBe(200);
      expect(Array.isArray(response.body)).toBe(true);
      expect(response.body.length).toBeGreaterThan(0);
      expect(response.body[0].id).toBe('R-1001');
      expect(response.body[0].userId).toBe('U100');
      expect(response.body[0].active).toBe(true);
    });
  });

  test('gets an empty list for a user without reservations', async () => {
    provider
      .given('user U200 has no reservations')
      .uponReceiving('a request for the reservations of U200')
      .withRequest({
        method: 'GET',
        path: '/users/U200/reservations'
      })
      .willRespondWith({
        status: 200,
        headers: { 'Content-Type': 'application/json' },
        body: []
      });

    await provider.executeTest(async (mockServer) => {
      process.env.RESERVATION_SERVICE_URL = mockServer.url;

      const response = await getReservationsByUser('U200');

      expect(response.status).toBe(200);
      expect(response.body).toEqual([]);
    });
  });
});
