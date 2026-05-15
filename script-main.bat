@echo off
setlocal

:: 1. Start rqueue-consumer and KEEP window open
start "rqueu-consumer" cmd /k "cd /d C:\Users\metet\Desktop\microservice-kafka-rqueue-mail-tests\rqueu\rqueu-consumer && mvn spring-boot:run"

:: 2. Start kafka-consumer and KEEP window open
start "kafkaConsumer" cmd /k "cd /d C:\Users\metet\Desktop\microservice-kafka-rqueue-mail-tests\kafka\kafkaConsumer && mvn package dependency:copy-dependencies -DskipTests && java -cp "target/classes;target/dependency/*" org.consumer.Main"

:: Wait for consumers to fully initialize
timeout /t 10 /nobreak

:: 3. Start rqueue-producer (closes normally after execution)
start "rqueue-producer" cmd /k "cd /d C:\Users\metet\Desktop\microservice-kafka-rqueue-mail-tests\rqueu\rqueu-producer && mvn spring-boot:run"

:: 4. Start kafka-producer (closes normally after execution)
start "kafka-producer" cmd /c "cd /d C:\Users\metet\Desktop\microservice-kafka-rqueue-mail-tests\kafka\kafkaProducer && mvn package dependency:copy-dependencies -DskipTests && java -cp "target/classes;target/dependency/*" org.producer.Main"

echo All services triggered. Consumers will stay active.
pause