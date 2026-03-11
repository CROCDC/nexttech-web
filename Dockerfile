FROM python:3.9-slim

WORKDIR /nexttech

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Crear directorio para uploads
RUN mkdir -p /nexttech/uploads/cv && chmod 777 /nexttech/uploads/cv

ENV FLASK_APP=run.py
ENV FLASK_ENV=production

EXPOSE 160
ENTRYPOINT []
CMD ["flask", "run", "--host=0.0.0.0", "--port=160"]
