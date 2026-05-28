@echo off
setlocal

:: 1. Start Rqueue consumer and keep the window open
start "rqueue-consumer" cmd /k "cd /d C:\Users\metet\Desktop\aws-version\rqueu\rqueu-consumer-new && mvn spring-boot:run"

:: 2. Start Kafka consumer and keep the window open
start "kafka-consumer" cmd /k "cd /d C:\Users\metet\Desktop\aws-version\kafka\kafkaConsumer-new && mvn clean compile exec:java -Dexec.mainClass=org.consumer.Main"

:: Wait 15 seconds for consumers to initialize
timeout /t 20 /nobreak

:: 3. Start Rqueue producer (closes after execution)
start "rqueue-producer" cmd /c "cd /d C:\Users\metet\Desktop\aws-version\rqueu\rqueu-producer-new && mvn spring-boot:run"

:: 4. Start Kafka producer (closes after execution)
start "kafka-producer" cmd /c "cd /d C:\Users\metet\Desktop\aws-version\kafka\kafkaProducer-new && mvn clean compile exec:java -Dexec.mainClass=org.producer.Main"

echo All services triggered. Consumers remain active.
pause