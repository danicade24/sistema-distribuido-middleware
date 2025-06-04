package sd.middleware;

import com.rabbitmq.client.Channel;
import com.rabbitmq.client.ConnectionFactory;
import com.rabbitmq.client.DeliverCallback;
// <-- OJO: NO importar com.rabbitmq.client.Connection -->
// import com.rabbitmq.client.Connection;

import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
// Tampoco importes java.sql.Connection si lo referencias totalmente cualificado
// import java.sql.Connection;

import java.nio.charset.StandardCharsets;

public class ValidadorDNI {
    public static void main(String[] args) throws Exception {
        // Conexión a RabbitMQ: usamos el nombre completo para evitar ambigüedad
        com.rabbitmq.client.Connection rabbitConn = new ConnectionFactory()
            .newConnection();
        Channel ch = rabbitConn.createChannel();
        ch.queueDeclare("validar_dni", true, false, false, null);
        ch.queueDeclare("validar_guardar_usuario", true, false, false, null);

        // Conexión a MariaDB: aquí usamos java.sql.Connection totalmente cualificado
        java.sql.Connection db = DriverManager.getConnection(
            "jdbc:mariadb://localhost:3306/bd2", "root", "root"
        );

        DeliverCallback callback = (consumerTag, message) -> {
            String json = new String(message.getBody(), StandardCharsets.UTF_8);
            String dni = json.replaceAll(".*\"dni\"\\s*:\\s*\"(\\d{8})\".*", "$1");
            boolean existe = false;

            // Validar en la tabla personas
            try (java.sql.PreparedStatement ps = db.prepareStatement(
                    "SELECT 1 FROM personas WHERE dni = ?"
                )) {
                ps.setString(1, dni);
                existe = ps.executeQuery().next();
            } catch (SQLException e) {
                e.printStackTrace();
            }

            if (existe) {
                ch.basicPublish("", "validar_guardar_usuario", null, message.getBody());
                System.out.println("DNI válido → reenviado: " + dni);
            } else {
                System.out.println("DNI no existe: " + dni);
            }
            ch.basicAck(message.getEnvelope().getDeliveryTag(), false);
        };

        ch.basicConsume("validar_dni", false, callback, tag -> {});
        System.out.println("Validador DNI escuchando…");
    }
}
