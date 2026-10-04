# Imagem de produção do frontend React/Vite.

# Bloco 1: instalar dependências e gerar os arquivos estáticos do Vite.
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# Bloco 2: servir o SPA e aplicar a configuração do nginx.
FROM nginx:alpine
RUN apk add --no-cache gettext
ENV BACKEND_URL=http://backend:8000
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["/bin/sh", "-c", "envsubst '${BACKEND_URL}' < /etc/nginx/conf.d/default.conf > /tmp/default.conf && cp /tmp/default.conf /etc/nginx/conf.d/default.conf && exec nginx -g 'daemon off;'"]
