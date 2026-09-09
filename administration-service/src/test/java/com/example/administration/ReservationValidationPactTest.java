package com.example.administration;

import au.com.dius.pact.consumer.MockServer;
import au.com.dius.pact.consumer.junit5.PactConsumerTestExt;
import au.com.dius.pact.consumer.junit5.PactTestFor;
import au.com.dius.pact.core.model.V4Pact;
import au.com.dius.pact.core.model.annotations.Pact;
import au.com.dius.pact.consumer.dsl.PactDslWithProvider;
import com.example.administration.admin.ReservationValidationController;
import com.example.administration.reservation.ReservationClient;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.web.client.RestClient;

import java.util.Map;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@ExtendWith(PactConsumerTestExt.class)
@PactTestFor(providerName = "Reservation Service")
class ReservationValidationPactTest {

    @Pact(consumer = "Administration Service")
    V4Pact activeReservationPact(PactDslWithProvider builder) {
        return builder
                .given("reservation R-1001 exists and is active")
                .uponReceiving("a request for active reservation R-1001")
                .path("/reservations/R-1001")
                .method("GET")
                .willRespondWith()
                .status(200)
                .headers(Map.of("Content-Type", "application/json"))
                .body("{\"active\":true}")
                .toPact(V4Pact.class);
    }

    @Pact(consumer = "Administration Service")
    V4Pact missingReservationPact(PactDslWithProvider builder) {
        return builder
                .given("reservation R-9999 does not exist")
                .uponReceiving("a request for missing reservation R-9999")
                .path("/reservations/R-9999")
                .method("GET")
                .willRespondWith()
                .status(404)
                .toPact(V4Pact.class);
    }

    @Test
    @PactTestFor(pactMethod = "activeReservationPact")
    void returnsValidTrueForAnActiveReservation(MockServer mockServer) throws Exception {
        mockMvc(mockServer)
                .perform(get("/admin/reservations/R-1001/valid"))
                .andExpect(status().isOk())
                .andExpect(content().contentTypeCompatibleWith(MediaType.APPLICATION_JSON))
                .andExpect(content().json("{\"valid\":true}"));
    }

    @Test
    @PactTestFor(pactMethod = "missingReservationPact")
    void returnsValidFalseForAMissingReservation(MockServer mockServer) throws Exception {
        mockMvc(mockServer)
                .perform(get("/admin/reservations/R-9999/valid"))
                .andExpect(status().isOk())
                .andExpect(content().contentTypeCompatibleWith(MediaType.APPLICATION_JSON))
                .andExpect(content().json("{\"valid\":false}"));
    }

    private MockMvc mockMvc(MockServer mockServer) {
        ReservationClient client = new ReservationClient(
                RestClient.builder().baseUrl(mockServer.getUrl()).build());
        return MockMvcBuilders.standaloneSetup(new ReservationValidationController(client)).build();
    }
}
