#!/bin/bash

# Construir la imagen Docker
sudo docker build -t chatserver . || exit 1

# Detener el contenedor existente
sudo docker stop chatserver-container || true

# Eliminar el contenedor existente
sudo docker rm chatserver-container || true

# Ejecutar un nuevo contenedor
sudo docker run -d --name chatserver-container -p 8000:8000 chatserver || exit 1

# Verificar que el contenedor esté en ejecución
sudo docker ps || exit 1

# Verificar los registros del contenedor
sudo docker logs chatserver-container || exit 1

