const amqp = require('amqplib');
const { faker } = require('@faker-js/faker');

async function main() {
    const connection = await amqp.connect('amqp://guest:guest@rabbitmq:5672');
    const channel = await connection.createChannel();
    const queue = 'validar_dni';

    await channel.assertQueue(queue, { durable: true });

    for (let i = 0; i < 1000; i++) {
        const nombre = faker.person.firstName();
        const correo = `usuario${i}@correo.com`;
        const clave = faker.internet.password(8);
        const dni = (60000000 + i).toString();  // Evita colisiones
        const telefono = (900000000 + i).toString(); // Único también

        const numAmigos = Math.floor(Math.random() * 5); // de 0 a 4 amigos
        const amigos = Array.from({ length: numAmigos }, () => 
            Math.floor(Math.random() * 50 + 1).toString()
        );

        const payload = {
            nombre,
            correo,
            clave,
            dni,
            telefono,
            amigos
        };

        channel.sendToQueue(queue, Buffer.from(JSON.stringify(payload)), { persistent: true });
        console.log(`Enviado usuario ${i + 1}: ${dni}`);
    }

    setTimeout(() => {
        connection.close();
        console.log("Terminó el envío masivo.");
    }, 1000);
}

main().catch(console.error);
