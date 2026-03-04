FROM nginx:alpine

COPY index.html /usr/share/nginx/html/index.html
COPY tenant-dashboard.html /usr/share/nginx/html/tenant-dashboard.html

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
