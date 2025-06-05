const amqp = require('amqplib');

const inquirer = require('inquirer');

async function main() {
    // Pedimos datos al cliente
    const datos = await inquirer.prompt([
        { name: 'nombre', message: 'Nombre: ' },
        { name: 'correo', message: 'Correo:' },
        { name: 'clave', message: 'Clave:' },
        { name: 'dni', message: 'DNI (8 digitos):' },
        { name: 'telefono', message: 'Telefono:' },
        { name: 'amigos', message: 'IDs de amigos (coma-separaods, opcional):' },
    ]);

    // Normalizar amigos
    datos.amigos = datos.amigos 
    ? datos.amigos.split(',').map(a => a.trim()).filter(a => a !== '') 
    : [];

    // conectar con RabbitMq
    const connection = await amqp.connect('amqp://guest:guest@rabbitmq:5672');
    const channel = await connection.createChannel();

    // garantizar que la cola exista y enviar mensaje persistente 
    const queue = 'validar_dni';
    await channel.assertQueue(queue, { durable: true });

    // enviar mensaje
    console.log('Enviando mensaje...');
    channel.sendToQueue(queue, Buffer.from(JSON.stringify(datos)), { persistent: true });
    console.log('Mensaje enviado');

    console.log('Datos enviados a la cola: ', queue);
    setTimeout(() => {
        connection.close();
    }, 500);
}

main().catch( err => {
    console.error('Error enviando: ', err);
    process.exit(1);
});