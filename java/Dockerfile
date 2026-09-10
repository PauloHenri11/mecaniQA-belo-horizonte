FROM eclipse-temurin:17-jdk-alpine

WORKDIR /app

COPY Main.java .

RUN javac --add-modules jdk.httpserver Main.java && \
    jar --create --file app.jar --main-class Main Main.class

EXPOSE 8080

CMD ["java", "--add-modules", "jdk.httpserver", "-jar", "app.jar"]