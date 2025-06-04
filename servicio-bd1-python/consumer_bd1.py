import json
import pika
import psycopg2
from concurrent.futures import ThreadPoolExecutor

# 1. Conexión a PostgreSQL (BD1)
pg_conn = psycopg2.connect(
    dbname="bd1",
    user="postgres",
    password="postgres",
    host="localhost",
    port=5432
)
pg_conn.autocommit = True

# Función que guarda un usuario en la tabla 'usuarios'
def guardar_usuario(data):
    # Extraer campos del JSON
    nombre   = data.get("nombre")
    correo   = data.get("correo")
    clave    = data.get("clave")
    dni      = data.get("dni")
    telefono = data.get("telefono")
    amigos   = data.get("amigos", [])  # lista de IDs (strings)

    # Convertir cada amigo a int, filtrar no-numéricos
    try:
        amigos_int = [int(a) for a in amigos if a.isdigit()]
    except Exception:
        amigos_int = []

    with pg_conn.cursor() as cur:
        # 2. Validar cuáles amigos existen en BD1
        if amigos_int:
            cur.execute(
                "SELECT id FROM usuarios WHERE id = ANY(%s)",
                (amigos_int,)
            )
            validos = [row[0] for row in cur.fetchall()]
        else:
            validos = []

        # 3. Insertar en la tabla usuarios
        cur.execute(
            """
            INSERT INTO usuarios (nombre, correo, clave, dni, telefono, amigos)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (nombre, correo, clave, dni, telefono, validos)
        )
    print(f"Guardado usuario {dni} (amigos válidos={len(validos)})")

# 4. Callback para consumir mensajes de RabbitMQ
def callback(ch, method, properties, body):
    data = json.loads(body)
    # Envío asíncrono a un pool de hilos para no bloquear el consumidor
    executor.submit(guardar_usuario, data)
    ch.basic_ack(delivery_tag=method.delivery_tag)

# 5. Configura ThreadPool (para concurrencia)
executor = ThreadPoolExecutor(max_workers=8)

# 6. Conexión a RabbitMQ y declaración de cola
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='validar_guardar_usuario', durable=True)

# Limitar cuántos mensajes pendientes puede tener el consumidor
channel.basic_qos(prefetch_count=10)
channel.basic_consume(
    queue='validar_guardar_usuario',
    on_message_callback=callback
)

print("Servicio BD1 escuchando...")
channel.start_consuming()
