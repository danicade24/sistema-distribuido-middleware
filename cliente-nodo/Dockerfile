# Imagen base oficial de Node.js
FROM node:22-slim

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos del cliente
COPY package*.json ./
RUN npm install

COPY . .

# Comando por defecto
CMD ["node", "simulated_sends.js"]
