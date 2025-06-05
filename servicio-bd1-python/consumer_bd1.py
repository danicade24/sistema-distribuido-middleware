import json
import time
import pika
import psycopg2
import threading
from psycopg2 import OperationalError

# Reintento para PostgreSQL
pg_conn = None
for i in range(15):
    try:
        pg_conn = psycopg2.connect(
            dbname="bd1",
            user="user",
            password="pass",
            host="bd1",
            port=5432
        )
        print("Conectado a PostgreSQL")
        break
    except OperationalError as e:
        print(f"[PostgreSQL] Intento {i+1}/15 fallido: {e}")
        time.sleep(5)
else:
    raise RuntimeError("No se pudo conectar a PostgreSQL")

# Reintento para RabbitMQ
rabbit_conn = None
for i in range(15):
    try:
        rabbit_conn = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        print("Conectado a RabbitMQ")
        break
    except pika.exceptions.AMQPConnectionError as e:
        print(f"[RabbitMQ] Intento {i+1}/15 fallido: {e}")
        time.sleep(5)
else:
    raise RuntimeError("No se pudo conectar a RabbitMQ")

# Función que guarda un usuario en la tabla 'usuarios'
def guardar_usuario(data):
    try:
        nombre   = data.get("nombre")
        correo   = data.get("correo")
        clave    = data.get("clave")
        dni      = data.get("dni")
        telefono = data.get("telefono")
        amigos   = data.get("amigos", [])

        try:
            amigos_int = [int(a) for a in amigos if a.isdigit()]
        except Exception:
            amigos_int = []

        with pg_conn.cursor() as cur:
            if amigos_int:
                cur.execute(
                    "SELECT id FROM usuarios WHERE id = ANY(%s)",
                    (amigos_int,)
                )
                validos = [row[0] for row in cur.fetchall()]
            else:
                validos = []

            cur.execute(
                """
                INSERT INTO usuarios (nombre, correo, clave, dni, telefono, amigos)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (nombre, correo, clave, dni, telefono, validos)
            )
            pg_conn.commit()
        print(f"Guardado usuario {dni} (amigos válidos={len(validos)})")
    except Exception as e:
        print(f"Error al guardar usuario {data.get('dni')}: {e}")

# Callback para consumir mensajes
def callback(ch, method, properties, body):
    data = json.loads(body)
    hilo = threading.Thread(target=guardar_usuario, args=(data,))
    hilo.start()
    ch.basic_ack(delivery_tag=method.delivery_tag)

# RabbitMQ consumer
channel = rabbit_conn.channel()
channel.queue_declare(queue='validar_guardar_usuario', durable=True)
channel.basic_qos(prefetch_count=10)
channel.basic_consume(queue='validar_guardar_usuario', on_message_callback=callback)

print("Servicio BD1 escuchando...")
channel.start_consuming()
