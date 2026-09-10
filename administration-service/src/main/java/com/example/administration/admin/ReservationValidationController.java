package com.example.administration.admin;

import com.example.administration.reservation.ReservationClient;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class ReservationValidationController {

    private final ReservationClient reservationClient;

    public ReservationValidationController(ReservationClient reservationClient) {
        this.reservationClient = reservationClient;
    }

    @GetMapping("/admin/reservations/{id}/valid")
    public ValidationResponse validateReservation(@PathVariable String id) {
        return new ValidationResponse(reservationClient.isReservationValid(id));
    }
}
