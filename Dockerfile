FROM alpine:3.18

# Instalar Apache y módulos necesarios
RUN apk add --no-cache apache2 apache2-utils

# Crear directorio para el sitio web
RUN mkdir -p /var/www/html

# Configurar Apache para servir archivos estáticos
RUN echo "ServerName localhost" >> /etc/apache2/httpd.conf && \
    sed -i 's#^DocumentRoot ".*#DocumentRoot "/var/www/html"#g' /etc/apache2/httpd.conf && \
    sed -i 's#^<Directory "/var/www">#<Directory "/var/www/html">#g' /etc/apache2/httpd.conf && \
    sed -i 's#^Options Indexes FollowSymLinks#Options -Indexes +FollowSymLinks#g' /etc/apache2/httpd.conf && \
    sed -i 's#^AllowOverride None#AllowOverride All#g' /etc/apache2/httpd.conf && \
    # Habilitar módulos necesarios
    sed -i 's#^#LoadModule rewrite_module modules/mod_rewrite.so\n#g' /etc/apache2/httpd.conf && \
    sed -i 's#^#LoadModule headers_module modules/mod_headers.so\n#g' /etc/apache2/httpd.conf

# Copiar los archivos del sitio web
COPY . /var/www/html/

# Exponer el puerto 80
EXPOSE 80

# Comando para iniciar Apache
CMD ["httpd", "-D", "FOREGROUND"] 