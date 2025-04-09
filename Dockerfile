FROM python:3.9-slim

WORKDIR /pantech

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Crear directorio para uploads
RUN mkdir -p /pantech/uploads/cv && chmod 777 /pantech/uploads/cv

ENV FLASK_APP=run.py
ENV FLASK_ENV=production

EXPOSE 160

CMD ["flask", "run", "--host=0.0.0.0", "--port=160"] 