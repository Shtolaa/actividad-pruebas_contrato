import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { PactV3, MatchersV3 } from '@pact-foundation/pact';
import { createReservation } from '../src/reservationClient.js';

const { regex } = MatchersV3;
const __dirname = path.dirname(fileURLToPath(import.meta.url));

const provider = new PactV3({
  consumer: 'Reservation App',
  provider: 'Reservation Service',
  dir: path.resolve(__dirname, '../../pacts')
});

describe('Reservation App contract', () => {
  test('creates a valid reservation', async () => {
    provider
      .given('a new valid reservation can be created')
      .uponReceiving('a request to create a valid reservation')
      .withRequest({
        method: 'POST',
        path: '/reservations',
        headers: { 'Content-Type': 'application/json' },
        body: {
          userId: 'U100',
          room: 'SALA-1',
          date: '2026-09-10',
          hours: 2
        }
      })
      .willRespondWith({
        status: 201,
        headers: { 'Content-Type': 'application/json' },
        body: {
          id: regex('R-[0-9]+', 'R-1001'),
          userId: 'U100',
          room: 'SALA-1',
          date: '2026-09-10',
          hours: 2,
          active: true
        }
      });

    await provider.executeTest(async (mockServer) => {
      const response = await createReservation(
        mockServer.url,
        'U100',
        'SALA-1',
        '2026-09-10',
        2
      );

      expect(response.status).toBe(201);
      expect(response.body.id).toBeDefined();
      expect(response.body.active).toBe(true);
    });
  });

  test('rejects an invalid reservation', async () => {
    provider
      .given('a new invalid reservation can be rejected')
      .uponReceiving('a request to create an invalid reservation')
      .withRequest({
        method: 'POST',
        path: '/reservations',
        headers: { 'Content-Type': 'application/json' },
        body: {
          userId: 'U100',
          room: 'SALA-1',
          date: '2026-09-10',
          hours: 0
        }
      })
      .willRespondWith({
        status: 400,
        headers: { 'Content-Type': 'application/json' },
        body: { error: 'INVALID_HOURS' }
      });

    await provider.executeTest(async (mockServer) => {
      const response = await createReservation(
        mockServer.url,
        'U100',
        'SALA-1',
        '2026-09-10',
        0
      );

      expect(response.status).toBe(400);
      expect(response.body).toEqual({ error: 'INVALID_HOURS' });
    });
  });
});
