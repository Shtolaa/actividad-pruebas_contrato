package com.example.administration.config;

import com.example.administration.reservation.ReservationClient;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestClient;

@Configuration
public class ReservationClientConfiguration {

    @Bean
    ReservationClient reservationClient(
            RestClient.Builder restClientBuilder,
            @Value("${RESERVATION_SERVICE_URL:http://localhost:8000}") String reservationServiceUrl) {
        return new ReservationClient(restClientBuilder.baseUrl(reservationServiceUrl).build());
    }
}
