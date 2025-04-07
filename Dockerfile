FROM alpine:3.18

# Instalar Apache
RUN apk add --no-cache apache2

# Crear directorio para el sitio web
RUN mkdir -p /var/www/html

# Copiar los archivos del sitio web
COPY . /var/www/html/

# Exponer el puerto 80
EXPOSE 80

# Comando para iniciar Apache
CMD ["httpd", "-D", "FOREGROUND"] 