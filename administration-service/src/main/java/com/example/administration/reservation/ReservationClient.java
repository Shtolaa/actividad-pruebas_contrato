package com.example.administration.reservation;

import org.springframework.http.ResponseEntity;
import org.springframework.web.client.RestClient;

public class ReservationClient {

    private final RestClient restClient;

    public ReservationClient(RestClient restClient) {
        this.restClient = restClient;
    }

    public boolean isReservationValid(String id) {
        ResponseEntity<ReservationStatus> response = restClient.get()
                .uri("/reservations/{id}", id)
                .retrieve()
                .onStatus(status -> status.value() == 404, (request, clientResponse) -> { })
                .onStatus(status -> status.value() != 200,
                        (request, clientResponse) -> {
                            throw new ReservationServiceException(clientResponse.getStatusCode().value());
                        })
                .toEntity(ReservationStatus.class);

        return response.getStatusCode().value() == 200
                && response.getBody() != null
                && response.getBody().active();
    }
}
