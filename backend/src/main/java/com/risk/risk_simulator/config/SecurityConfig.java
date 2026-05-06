package com.risk.risk_simulator.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.web.SecurityFilterChain;

import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.provisioning.InMemoryUserDetailsManager;

@Configuration
@EnableMethodSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {

        http
            .csrf(csrf -> csrf.disable())

            .authorizeHttpRequests(auth -> auth

                .requestMatchers(
                        "/auth/**",
                        "/swagger-ui/**",
                        "/v3/api-docs/**"
                ).permitAll()

                .requestMatchers("/admin/**").hasRole("ADMIN")

                .anyRequest().authenticated()
            )

            .exceptionHandling(ex -> ex
                .authenticationEntryPoint((request, response, authException) -> {
                    response.sendError(401, "Unauthorized");
                })
            )

            .httpBasic(httpBasic -> {});

        return http.build();
    }

    @Bean
    public UserDetailsService users() {

        UserDetails user = User.withDefaultPasswordEncoder()
                .username("user")
                .password("user123")
                .roles("USER")
                .build();

        return new InMemoryUserDetailsManager(user);
    }
}