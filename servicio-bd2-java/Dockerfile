FROM maven:3.9.9-eclipse-temurin-24-noble AS builder
WORKDIR /build
COPY validador-dni/ .
RUN mvn clean package

FROM openjdk:25-jdk-slim
WORKDIR /app
COPY --from=builder /build/target/validador-dni-*.jar app.jar
CMD ["java", "-jar", "app.jar"]