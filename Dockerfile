# Usar una imagen oficial y ligera de Python
FROM python:3.11-slim

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar e instalar las dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código fuente y carpetas (backend, frontend, data) al contenedor
COPY . .

# Exponer el puerto 5000 donde corre Flask
EXPOSE 5000

# Comando para iniciar la aplicación web
CMD ["python", "backend/app.py"]