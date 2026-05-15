package org.rqueue;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import java.util.concurrent.atomic.AtomicInteger;

@SpringBootApplication
public class RqueuConsumerApplication {

    public static final AtomicInteger messageCounter = new AtomicInteger(0);
    public static final int TOTAL_EXPECTED_MESSAGES = 550;

    public static void main(String[] args) {
        SpringApplication.run(RqueuConsumerApplication.class, args);
    }

}
