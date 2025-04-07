FROM alpine:3.18

# Instalar Nginx
RUN apk add --no-cache nginx

# Crear directorio para el sitio web
RUN mkdir -p /var/www/html

# Configurar Nginx
RUN echo 'server { \
    listen 80; \
    server_name localhost; \
    root /var/www/html; \
    index index.html; \
    location / { \
        try_files $uri $uri/ /index.html; \
        add_header Cache-Control "no-cache"; \
        add_header X-Content-Type-Options "nosniff"; \
        add_header X-Frame-Options "SAMEORIGIN"; \
        add_header X-XSS-Protection "1; mode=block"; \
    } \
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ { \
        expires 1y; \
        add_header Cache-Control "public, no-transform"; \
    } \
    error_page 404 /index.html; \
    error_log /var/log/nginx/error.log debug; \
    access_log /var/log/nginx/access.log combined; \
}' > /etc/nginx/http.d/default.conf

# Copiar archivos del sitio web
COPY . /var/www/html/

# Establecer permisos correctos
RUN chown -R nginx:nginx /var/www/html && \
    chmod -R 755 /var/www/html && \
    mkdir -p /var/log/nginx && \
    chown -R nginx:nginx /var/log/nginx && \
    chmod -R 755 /var/log/nginx

# Exponer puerto 80
EXPOSE 80

# Iniciar Nginx
CMD ["nginx", "-g", "daemon off;"] 