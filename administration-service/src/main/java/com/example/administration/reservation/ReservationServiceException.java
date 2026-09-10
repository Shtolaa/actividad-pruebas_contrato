package com.example.administration.reservation;

public class ReservationServiceException extends RuntimeException {

    public ReservationServiceException(int statusCode) {
        super("Reservation service returned unexpected status " + statusCode);
    }
}
