#!/bin/bash

echo "=== Iniciando pipeline local ==="

# Stage: Checkout
echo "=== Stage: Checkout ==="
echo "Directorio actual: $(pwd)"
echo "Usuario actual: $(whoami)"
echo "Contenido del directorio:"
ls -la

# Stage: Deploy
echo "=== Stage: Deploy ==="
echo "Deteniendo contenedores existentes..."
docker compose down

echo "Construyendo y levantando contenedores..."
docker compose up -d --build

echo "Esperando a que el contenedor esté listo..."
sleep 10

echo "Verificando estado del contenedor..."
docker ps | grep pantech-web

echo "Verificando configuración de Nginx..."
docker exec pantech-web nginx -t

echo "Verificando logs de Nginx..."
docker exec pantech-web tail -n 50 /var/log/nginx/error.log

echo "Verificando acceso al sitio..."
curl -v http://localhost:160

echo "=== Pipeline completado ===" 