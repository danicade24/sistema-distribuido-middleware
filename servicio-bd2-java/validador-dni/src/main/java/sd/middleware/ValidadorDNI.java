package sd.middleware;

import com.rabbitmq.client.*;
import java.sql.*;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.regex.*;

public class ValidadorDNI {

    public static void main(String[] args) throws Exception {
        // Conexión a RabbitMQ
        ConnectionFactory factory = new ConnectionFactory();
        factory.setHost("rabbitmq");
        factory.setPort(5672);

        com.rabbitmq.client.Connection rabbitConn = null;
        int retries = 60;
        while (retries-- > 0) {
            try {
                rabbitConn = factory.newConnection();
                break;
            } catch (Exception e) {
                System.out.println("RabbitMQ no disponible, reintentando...");
                Thread.sleep(5000);
            }
        }

        if (rabbitConn == null) throw new RuntimeException("No se pudo conectar a RabbitMQ");

        Channel ch = rabbitConn.createChannel();
        ch.queueDeclare("validar_dni", true, false, false, null);
        ch.queueDeclare("validar_guardar_usuario", true, false, false, null);

        // Conexión a MariaDB
        java.sql.Connection db = DriverManager.getConnection("jdbc:mariadb://bd2:3306/bd2", "root", "root");

        // Callback
        DeliverCallback callback = (consumerTag, message) -> {
            new Thread(() -> {
                String json = new String(message.getBody(), StandardCharsets.UTF_8);
                long tag = message.getEnvelope().getDeliveryTag();

                // Extraer DNI con expresión regular
                Matcher m = Pattern.compile("\"dni\"\\s*:\\s*\"(\\d{8})\"").matcher(json);
                if (!m.find()) {
                    System.out.println("DNI no encontrado en: " + json);
                    ack(ch, tag);
                    return;
                }

                String dni = m.group(1);
                boolean existe = false;

                try (PreparedStatement ps = db.prepareStatement("SELECT 1 FROM personas WHERE dni = ?")) {
                    ps.setString(1, dni);
                    existe = ps.executeQuery().next();
                } catch (SQLException e) {
                    System.err.println("Error al validar DNI " + dni);
                    e.printStackTrace();
                }

                if (existe) {
                    try {
                        ch.basicPublish("", "validar_guardar_usuario", null, message.getBody());
                        System.out.println("✅ DNI válido → reenviado: " + dni);
                    } catch (IOException e) {
                        System.err.println("Error reenviando mensaje: " + e.getMessage());
                    }
                } else {
                    System.out.println("❌ DNI no existe: " + dni);
                }

                ack(ch, tag);
            }).start();
        };

        ch.basicConsume("validar_dni", false, callback, tag -> {});
        System.out.println("🟢 Validador DNI escuchando…");
    }

    // Asegura que el ack se haga incluso si hay errores
    private static void ack(Channel ch, long tag) {
        try {
            ch.basicAck(tag, false);
        } catch (IOException e) {
            System.err.println("Error haciendo ACK del mensaje:");
            e.printStackTrace();
        }
    }
}
