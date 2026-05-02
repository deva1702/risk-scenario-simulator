package com.internship.tool.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.Map;

@Service
public class AiServiceClient {

    // Logger for better error tracking (instead of System.out)
    private static final Logger logger = LoggerFactory.getLogger(AiServiceClient.class);

    private final RestTemplate restTemplate;

    // Base URL of Flask AI service
    private static final String AI_BASE_URL = "http://localhost:5000";

    // Constructor injection (best practice)
    public AiServiceClient(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    /**
     * Calls Flask AI endpoint with input text
     * Returns response body if successful, else null
     */
    public String callTestEndpoint(String input) {
        try {
            String url = AI_BASE_URL + "/test";

            // Prepare request body
            Map<String, String> body = new HashMap<>();
            body.put("input", input);

            // Set headers
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);

            // Combine headers and body into request entity
            HttpEntity<Map<String, String>> request =
                    new HttpEntity<>(body, headers);

            // Make POST request
            ResponseEntity<String> response = restTemplate.exchange(
                    url,
                    HttpMethod.POST,
                    request,
                    String.class
            );

            // Return only if response is successful (2xx)
            if (response.getStatusCode().is2xxSuccessful()) {
                return response.getBody();
            } else {
                return null;
            }

        } catch (RestClientException e) {
            // Graceful failure with logging
            logger.error("AI Service call failed: {}", e.getMessage());
            return null;
        }
    }
}