FROM node:22-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
ARG VITE_API_URL=https://backend-production-15ec.up.railway.app/api
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

EXPOSE 4173
CMD ["sh", "-c", "npm run preview -- --host 0.0.0.0 --port ${PORT:-4173}"]
