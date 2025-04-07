FROM alpine:latest

# Instalar un servidor web ligero (httpd)
RUN apk add --no-cache httpd

# Copiar los archivos del sitio web
COPY . /var/www/localhost/htdocs/

# Exponer el puerto 80
EXPOSE 80

# Comando para iniciar el servidor web
CMD ["httpd", "-D", "FOREGROUND"] 