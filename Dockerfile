FROM nginx:alpine

COPY index.html /usr/share/nginx/html/index.html
COPY og-image.png /usr/share/nginx/html/og-image.png
COPY data /usr/share/nginx/html/data

EXPOSE 80
