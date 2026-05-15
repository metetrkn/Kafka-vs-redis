package org.consumer;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import java.io.IOException;
import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.stream.Collectors;

public class EmailSender {

    private static final Logger logger = LoggerFactory.getLogger(EmailSender.class);
    private static final String WIREMOCK_URL = "http://localhost:9090/v1/send-email";
    private static final String API_KEY = "api:key-fake";
    private static final String FROM_EMAIL = "sender@example.com";

    private static final HttpClient client = HttpClient.newBuilder()
            .version(HttpClient.Version.HTTP_2)
            .connectTimeout(Duration.ofSeconds(10))
            .build();


    public static class EmailRequest {
        public String to;
        public String subject;
        public String body;
        public long creationTime;
        public String topic;
        public int consumerId;

        public EmailRequest(String to, String subject, String body, long creationTime, String topic, int consumerId) {
            this.to = to;
            this.subject = subject;
            this.body = body;
            this.creationTime = creationTime;
            this.topic = topic;
            this.consumerId = consumerId;
        }
    }

    public static void sendBatch(List<EmailRequest> batch) {
        if (batch == null || batch.isEmpty()) return;

        List<CompletableFuture<Void>> futures = batch.stream()
                .map(email -> sendAsync(email))
                .collect(Collectors.toList());

        CompletableFuture.allOf(futures.toArray(new CompletableFuture[0])).join();
    }

    private static CompletableFuture<Void> sendAsync(EmailRequest email) {
        String formData = buildFormData(email.to, email.subject, email.body);

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(WIREMOCK_URL))
                .header("Content-Type", "application/x-www-form-urlencoded")
                .header("Authorization", "Basic " + java.util.Base64.getEncoder().encodeToString(API_KEY.getBytes()))
                .POST(HttpRequest.BodyPublishers.ofString(formData))
                .timeout(Duration.ofSeconds(10))
                .build();

        return client.sendAsync(request, HttpResponse.BodyHandlers.ofString())
                .thenAccept(response -> {
                    if (response.statusCode() == 200) {
                        long sentTime = System.currentTimeMillis();
                        int currentCount = Main.messageCounter.incrementAndGet();
                        logger.info("Topic: {} | Consumer: {} | Sent to: {} | Created: {} | Sent: {}",
                                email.topic, email.consumerId, email.to, email.creationTime, sentTime);

                        if (currentCount == Main.TOTAL_EXPECTED_MESSAGES) {
                            try {
                                // Run the second script
                                Runtime.getRuntime().exec("cmd /c start script-2.bat");

                                // Small buffer to ensure the OS registers the process start
                                Thread.sleep(1000);

                                // Kill the Java process
                                System.exit(0);
                            } catch (IOException e) {
                                throw new RuntimeException(e);
                            } catch (InterruptedException e) {
                                throw new RuntimeException(e);
                            }
                        }
                    }
                });
    }

    private static String buildFormData(String to, String subject, String body) {
        return "from=" + encode(FROM_EMAIL) +
                "&to=" + encode(to) +
                "&subject=" + encode(subject) +
                "&text=" + encode(body);
    }

    private static String encode(String value) {
        return URLEncoder.encode(value, StandardCharsets.UTF_8);
    }
}