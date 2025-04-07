FROM alpine:3.18

# Instalar Apache y utilidades
RUN apk add --no-cache apache2 apache2-utils

# Crear directorio para el sitio web
RUN mkdir -p /var/www/html

# Configurar Apache
RUN echo "ServerName localhost" >> /etc/apache2/httpd.conf && \
    sed -i 's#^DocumentRoot ".*#DocumentRoot "/var/www/html"#g' /etc/apache2/httpd.conf && \
    sed -i 's#^<Directory "/var/www">#<Directory "/var/www/html">#g' /etc/apache2/httpd.conf && \
    sed -i 's#^Options Indexes#Options -Indexes +FollowSymLinks#g' /etc/apache2/httpd.conf && \
    sed -i 's#^AllowOverride None#AllowOverride All#g' /etc/apache2/httpd.conf && \
    echo -e '<Directory "/var/www/html">\n\
    Options -Indexes +FollowSymLinks\n\
    AllowOverride All\n\
    Require all granted\n\
    DirectoryIndex index.html\n\
</Directory>' >> /etc/apache2/httpd.conf

# Habilitar módulos necesarios
RUN sed -i 's/#LoadModule rewrite_module/LoadModule rewrite_module/' /etc/apache2/httpd.conf && \
    sed -i 's/#LoadModule headers_module/LoadModule headers_module/' /etc/apache2/httpd.conf

# Copiar archivos del sitio web
COPY . /var/www/html/

# Establecer permisos correctos
RUN chown -R apache:apache /var/www/html && \
    chmod -R 755 /var/www/html && \
    chmod 644 /var/www/html/index.html

# Exponer puerto 80
EXPOSE 80

# Iniciar Apache
CMD ["httpd", "-D", "FOREGROUND"] 