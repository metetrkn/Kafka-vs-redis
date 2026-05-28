# KAFKA - RQUEUE - MICROSERVICE - TEST - MAIL SERVICE

## Project Overview
- This project provides comprehensive benchmarking of Apache Kafka and Redis Queue with Spring Boot (JDK 17) to test precise configuration tuning for a scalable and resilient high-throughput email architecture. 
- The project consists of two main parts: kafka/ and rqueue/, each containing its own test cases, reporting, documentation, codebase, and related materials.
- This README.md provides documentation for both Kafka and RQueue, while each subproject also includes its own README.md file within its respective folder.

## Overall Architecture
The project includes a remote orchestration layer to trigger test runs and visualize results, connecting a cloud-based web interface with the local testing environment.

![Overall System Architecture](overall-schema.png)

### Workflow
1.  **Test Execution Trigger**: A user interacts with a web application hosted on AWS Elastic Beanstalk (EBS) to start a test run.
2.  **Request Tunneling**: The web app sends an HTTP POST request to the local environment via an `ngrok` public bridge. This allows the cloud application to securely communicate with the local machine.
3.  **Local Worker**: A `Node.js` worker on the local machine listens for incoming requests from ngrok.
4.  **Script Execution**: Upon receiving a request, the Node.js worker executes `script-main.bat`, which initiates the message producers (for either Kafka or RQueue).
5.  **Benchmarking Run**: The producers and consumers for the selected message broker (Kafka or RQueue/Redis) run the benchmark test.
6.  **Log Analysis**: After the test completes, `script-2.bat` is executed, which runs the Python log analysis application (`PYTHON APP ANALYS`).
7.  **Result Visualization**: The Python script processes the logs, generates analysis data, and sends it back as an HTTP response to the AWS web application, where the results are visualized for the user.

---

<br><br>

# A- Kafka Email-Message Broker Processing Project
## Project Overview
This project conducts comprehensive benchmarking of Apache Kafka to identify the precise configuration tuning required for a scalable and resilient high-throughput email architecture.
Key Tuning Parameters:
 - Partition count
 - Consumer count
 - Worker threads
 - Batch size

Output: Metrics and logs are stored in the TEST RESULTS directory. There are three main output artifacts:
  - log_report.csv: Contains detailed performance metrics per consumer.
  - report.png: Visualizes log_report.csv, with consumers grouped by topic.
  - test-doc.txt: Summary of configuration parameters, analysis, and conclusions.

---

## How to utilize
 1- Check the test cases in TEST-CASE/ to observe the parameters and their effects on performance.
 2- You may retest the same parameters—or try additional ones—to gather further insights.

---

## Refined Insights from tests
- 1> Maintain a 1:1:1 Ratio Ensure 1 partition = 1 consumer = 1 thread for maximum resource utilization.
- 2> Maximize Batch Sizes within Global Limits Target large batches, but strictly cap total processing capacity: (Total High Consumers × High Batch) + (Total Low Consumers × Low Batch) < 800
- 3> Tune Polling Frequency by Priority Reduce polling on low-priority topics to save resources, but keep high-priority polling frequent. (Avoid over-polling empty queues).
- 4> Manage Concurrency & API Limits Batch size directly correlates to the number of open HTTP sockets. If simultaneous requests exceed Mailgun's concurrency limit, you will trigger "Too Many Requests" errors.
- 5> Production Tuning Levers
	- If System Overloaded (CPU/RAM): Scale down high-priority concurrency (e.g., reduce partitions/consumers from 6 → 
	- If API Rate Limited (Mailgun): Decrease the batch size for low-priority topics first

---

## How the System Works

### Producer (kafkaProducer)
- **Concurrency**: Utilizes 2 asynchronous threads to publish messages to Kafka topics.
- **Topics**:
- **Message Publishing**:
      <In most cases, number of mails as follows, it may vary.>
  - **High Topic**: Publishes a total of 11,000 messages.
  - **Low Topic**: Publishes a total of 111,000 messages.

---

#### Detailed Operation
- **Threading**: In kafkaProducer there are 2 threads, each responsible for asynchronously sending messages to Kafka.
- **Batch Processing**: Messages are grouped and sent in batches for efficiency. (Number of batches per topic in most scenarios: High (50) for pace, Low (200) for efficiency).
- **Message Content**: Each message includes a unique ID, timestamp, and payload (e.g., email data).
- **Error Handling**: Processing errors are logged; failed messages may be retried or skipped based on logic.

---

### Consumer (javaConsumer)
The system supports customizable performance scenarios by parameterizing key metrics such as consumer count, worker thread pool size, batch size, poll frequency, and topic partition count. These configurations are centralized in javaConsumer/Main.java.

---

#### Detailed Operation
- **Partition Assignment**: For high-throughput topics, each consumer instance is assigned to a unique partition, ensuring parallel processing.
- **Threading**: Each consumer runs in its own thread, polling Kafka and processing batches.
- **Batch Processing**: Messages are processed in batches (size and poll interval configurable per topic). Finding the ideal batch size for both efficiency and pace is a primary test case.
- **Email Sending**: Each message invokes the EmailSender to asynchronously dispatch emails via HTTP and log the outcome. For testing, the external API is mocked using a containerized WireMock instance.
- **Offset Management**: Offsets are committed after successful batch processing to ensure at-least-once delivery.
---

### Log-Analyzer
- **Parsing**: log-analyzer/log-analyzer.py parses consumer logs (javaConsumer/logs/email-consumer.log) to extract metrics: topic, consumer ID, throughput, execution times (avg/max), and error counts.
- **Report per Consumer**: Aggregates parsed data to generate log_report.csv.
- **Report per Topic**: Generates a high-level summary grouping all consumers by topic.
- **Metric Calculation**: Calculates throughput, error rates, batch statistics, and end-to-end latency.
- **Visualization**: log-analyzer/visualize.py renders performance plots and saves them to /log-analyzer/report.png.

## Example Message Lifecycle

1. **Producer Thread** creates a message with a unique ID and timestamp, and sends it to the Kafka broker.
2. **Kafka Broker** stores the message in the appropriate topic partition.
3. **Consumer Thread** polls the partition, retrieves a batch, and processes each message (e.g., sends an email).
4. **Processing Event** is logged with timestamps for received, processed, and sent.
5. **Log Analyzer** parses the logs, calculates the latency for each message, and generates reports.
6. **Visualization** scripts create charts for further analysis.

---

## Folder Structure

```
javaConsumer/
  └─ javaConsumer/
      ├─ pom.xml
      ├─ logs/
      ├─ src/
      │   └─ main/java/org/consumer/
      │        ├─ EmailSender.java
      │        ├─ KafkaEmailConsumer.java
      │        └─ Main.java
      │   └─ resources/logback.xml
      └─ target/
kafkaProducer/
  ├─ pom.xml
  └─ src/main/java/org/producer/Main.java
log-eval/
  ├─ log_report.csv
  ├─ log-analyzer.py
  ├─ state.json
  ├─ time_report.csv
  └─ visualize.py
TEST RESULTS/
  └─ TEST1/ ... TEST7/
      ├─ log_report.csv
      ├─ testX-doc.txt
      └─ scnerio1.txt
```

---

## Prerequisites
- **Java SDK 17** and **Maven** for building and running producer/consumer modules.
- **Python 3.14** and related import libraries for log analysis.
- **Kafka** cluster or docker running and accessible.
- **Email server** Wiremock Docker image wiremock/wiremock:latest
---

## Setup & Usage

### 1. Start Kafka
Ensure your Kafka broker is running and accessible. Update connection details in both producer and consumer modules.

### 2. Build and Run Producer
```
cd kafkaProducer
mvn clean package
java -cp target/classes org.producer.Main
or simply run Main.java from IDE
```

### 3. Build and Run Consumer
```
cd javaConsumer/javaConsumer
mvn clean package
java -cp target/classes org.consumer.Main
or simply run Main.java from IDE
OBS!: Running the consumer first is generally considered best practice, even though published messages are logged in Kafka partitions. Starting the consumer first can improve performance. Kafka consumers continue to run and process messages in partitions until they crash or are explicitly closed.
```

### 4. Analyze Logs
```
cd log-eval
python log-analyzer.py
python visualize.py
```

### 5. Review Test Results
Check the `TEST RESULTS` folder for scenario-specific logs and documentation.

---

## Module Details (Deep Dive)

### 1. kafkaProducer
- **Purpose**: Publishes messages (e.g., email events) to a Kafka topic.
- **Key File**: `src/main/java/org/producer/Main.java`
- **Build**: Uses Maven (`pom.xml`).
- **How to Run**:
  1. Navigate to the `kafkaProducer` directory.
  2. Build: `mvn clean package`
  3. Run: `java -cp target/classes org.producer.Main`
  4. Or simply run IDE Run button.
- **Configuration**: Update Kafka broker and topic details in the source code or configuration files as needed.

---

### 2. javaConsumer
- **Purpose**: Consumes messages from Kafka and processes them (e.g., sends emails).
- **Key Files**: EmailSender.java: Handles asynchronous HTTP email sending using concurrent socket connections. 
    - Constraint: The operating system's file descriptor limit (typically 1024) restricts the maximum number of concurrent connections.Calculation: Total sockets = $\sum (Consumers \times BatchSize)$.
    - Example: (5 high-pace consumers × 50 batch) + (2 low-pace consumers × 200 batch) = 650 concurrent connections.
    - Warning: If this number approaches 1000, you risk Too many open files errors due to file descriptor exhaustion.KafkaEmailConsumer.java: 
    - Implementation of the Kafka consumer logic.Main.java: Application entry point.WireMock: Initializes stubs (requires correct email schema validation to avoid request failures).Graceful Shutdown: Ensures Kafka offsets are committed before exit. 
    Abrupt termination causes offset mismatches and message duplication on restart.
- **Logging**: 
    - Config: Controlled by logback.xml.
    - Storage: Logs are written to the logs/ directory.
- **How to RunNavigate**: 
    1. Go to javaConsumer/javaConsumer.
    2. Build: Run mvn clean package.
    3. Run: Execute java -jar target/<your-jar-name>.jar.
- **Configuration**:
    - Update Kafka and email server settings directly in the source code or within the resources directory.

---

### 3. log-eval
- **Purpose**: Analyzes logs generated by the consumer and produces reports.
- **Key Files**:
  - `log-analyzer.py`: Main log analysis script.
  - `visualize.py`: Visualization of log data.
  - `log_report.csv`, `time_report.csv`: Output reports.
- **How to Use**:
  1. Ensure Python 3 is installed.
  2. Install dependencies (if any): `pip install -r requirements.txt` (create if needed).
  3. Run analysis: `python log-analyzer.py`
  4. Visualize: `python visualize.py`
  5. Or simply run related python file from IDE.

---

### 4. TEST RESULTS
- **Purpose**: Stores results from various test scenarios.
- **Latency Calculation**: 
      - End-to-End Latency: Time difference between producer's publish timestamp and consumer's processing timestamp.
      - Batch Latency: Average, min, and max latencies computed per batch.
---

## Customization
- **Mail Sender Service:**: Configure javaConsumer/EmailSender.java such as url, api-key, from-email, connection timeout and other mail service related details.
- **Message Volume:**: Configure the total number of test messages in kafkaProducer/Main.java.
- **Consumer Settings:**: Adjust consumer count, worker threads, poll frequency, and batch limits in javaConsumer/Main.java.
- **Service Stubbing**: Define the WireMock message sender schema in javaConsumer/Main.java.
- **Graceful Shutdown**: Configure shutdown timeouts and offset commit logic in javaConsumer/Main.java.
- **Logging**: Modify log levels and retention in `logback.xml`.
- **Partitions**: Manually configure partition counts via the Kafka CLI. 
Note: Align the number of consumers and worker threads with the partition count to optimize parallelism (Recommended ratio: 1 Consumer per Partition).

---

## Troubleshooting
- Ensure Kafka is up and running.
- Ensure the WireMock instance is active and the port is correctly exposed (Default mapping: 8080:8080).
- Check logs for errors in `logs/` and `log-eval/`.
- Verify Java and Python versions.

---
<br><br>

# B- RQueue Email-Message Processing Project
## Project Overview
This project benchmarks and analyzes the performance of RQueue as a message broker for scalable, reliable, and high-throughput email delivery systems. The goal is to identify optimal configuration parameters and architectural patterns for robust email processing using RQueue.
- Number of mails published in producer

---

## How to utilize
 1- Check the test cases in TEST-CASE/ to observe the parameters and their effects on performance.
 2- You may retest the same parameters—or try additional ones—to gather further insights.


---

## Project Structure

```
rqueu/
├── log-eval/
│   ├── log-analyzer.py
│   ├── log_report.csv
│   ├── state.json
│   └── visualize.py
├── rqueu-consumer/
│   ├── .idea/
│   ├── .mvn/
│   ├── HELP.md
│   ├── logs/
│   ├── mvnw
│   ├── mvnw.cmd
│   ├── pom.xml
│   ├── src/
│   └── target/
├── rqueu-producer/
│   ├── .idea/
│   ├── .mvn/
│   ├── HELP.md
│   ├── mvnw
│   ├── mvnw.cmd
│   ├── pom.xml
│   ├── src/
│   └── target/
├── sharedDTO/
│   ├── .gitignore
│   ├── .idea/
│   ├── pom.xml
│   └── src/
├── TEST-CASE/
│   ├── TEST-1/
│   ├── TEST-2/
│   ├── TEST-3/
│   ├── TEST-4/
│   ├── TEST-5/
│   └── TEST-6/
└── README.md
```

---

**Logs:**
- Logs are located at rqueue-consumer/logs/email-consumer.log.
- The log-eval (Python) project retrieves these logs to generate outputs.

**Output:**
- Metrics and logs are stored in the results directory, including:
  - `log_report.csv`: Detailed performance metrics per queu
  - `report.png`: Visualization of performance data
  - `Result.txt`: Summary of configuration, analysis, and findings

---

## Insights & Best Practices
- **Concurrency Management:** 
 - Different ranges of concurrency per queue were tested, and as seen in the results (TEST-5/RESULT.txt and concurrency_analysis.png), the configuration of 10–20 concurrency for high-priority and 5–10 for low-priority provides the best overall performance—especially for high-priority emails, but also for low-priority ones.

 - Increasing concurrency does not always lead to better performance. As shown in concurrency_analysis.png, even though resources are doubled, the performance boost decreases once concurrency is set above 5–10 for standard emails.

 - Assigning too much concurrency to the low-priority queue steals resources from the high-priority queue; therefore, a balance between the queues is required.

 - When the workload ratio is approximately 1:10, the optimal concurrency allocation observed was 2/1 for high/low priority queues.

---

## System Architecture
### Producer
- By default, the producer publishes messages synchronously in Redis.
- There is no batching by default. This is the default behavior in Redis and in this project as well.
- Publishes email messages to RQueue queues asynchronously.
- Supports configurable batch sizes and message rates.
- Each message includes unique identifiers and payload data (from, to, subject, fake body message, created timestamp).
- There are 2 different type of subjects that mails can contain (STANDART and VIP)

### Consumer
- By default, consumers act asynchronously, racing to handle incoming messages from the queue.
- There is no batching by default. This is the default behavior in Redis and in this project as well.
- Multiple consumers/workers process messages in parallel from RQueue.
- Each message triggers an email send operation (WireMock - fake).
- Offsets and acknowledgments ensure reliable delivery.

### Shared DTO
 - The sharedDTO/ folder contains a file EmailDTO.java, which represents the schema of an email. It is used by both the producer and consumer via dependency injection.
 - The shared DTO is located in the .m2 folder, where Maven stores shared packages.
 - Run the command `mvn install` from the sharedDTO directory to generate the .class files.
 - After that, add the credentials from the pom.xml of the related import file—in this case, for both the producer and consumer.
---

## Configurations
1. In application.properties, keep rqueue.scheduler.auto-start=false; otherwise, stubbing may not work because the consumer could start listening to messages too early, causing errors or missed messages.
- Make sure to set the Redis and mail sender service WireMock host, port, API key, and URL appropriately.
2. rqueu-consumer/consumer/EmailConsumer.java: Set concurrencyHigh and concurrencyLow for different performance results.


## How to Run Tests
1. Ensure to set all configurations properly.
2. Start the producer to enqueue messages.
3. Launch consumers to process the queue. It is generally better to start consumers first, even though published messages wait in the Redis queue (RAM) until consumed. Be aware that if the system crashes while messages are still in RAM, data may be lost.
4. Analyze output metrics and logs in the results directory. (Run log-eval/log-analyzer.py and visualize.py)

---

## Results & Analysis
- Review `log_report.csv` and `Result.txt` for detailed performance data and conclusions.
- Use `report.png` for a visual summary of throughput and resource utilization.

---

## Prerequisites
- **Java SDK 17** and **Maven** for building and running producer/consumer modules.
- **Python 3.14** and related import libraries for log analysis.
- **Rqueu** cluster or docker running and accessible image redis:latest.
- **Email server** Wiremock Docker image wiremock/wiremock:latest
---

## Review Test Results
Check the `TEST RESULTS` folder for scenario-specific logs and documentation.

---

## License
This project is licensed under the MIT License. Copyright © 2026.

---

## Authors
- Mete Turkan
- metetrkn52@gmail.com
- https://www.linkedin.com/in/mete-turkan/
---