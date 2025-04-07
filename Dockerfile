FROM alpine:3.18

# Instalar un servidor web ligero (httpd)
RUN apk add --no-cache apache2

# Copiar los archivos del sitio web
COPY . /var/www/localhost/htdocs/

# Exponer el puerto 80
EXPOSE 80

# Comando para iniciar el servidor web
CMD ["httpd", "-D", "FOREGROUND"] 