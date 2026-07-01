# Этап сборки — компилируем React-приложение
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci --no-audit --no-fund

COPY . .
RUN npm run build

# Этап раздачи статики через Nginx
FROM nginx:1.27-alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

# Liveness-проба: проверяем, что nginx отвечает на главную страницу.
# Используем 127.0.0.1, а не localhost: внутри контейнера localhost резолвится
# в IPv6 (::1), а nginx слушает только IPv4 — из-за этого проба ложно падала.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget --spider -q http://127.0.0.1/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
