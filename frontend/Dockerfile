# --- Stage 1: Build the React/Vite SPA ---
FROM node:22-alpine AS builder

WORKDIR /app

# Copy root workspace configurations and package files
COPY package.json package-lock.json ./
COPY packages/api-types/package.json ./packages/api-types/
COPY frontend/package.json ./frontend

# Install all dependencies (inclding workspace packages)
RUN npm ci

# Copy the rest of the source code
COPY packages/api-types/ ./packages/api-types/
COPY frontend/ ./frontend/

# Build the frontend application
WORKDIR /app/frontend
RUN npm run build

# --- Stage 2: Serve with Nginx ---
FROM nginx:1.27-alpine AS runtime

# Copy build assets from builder stage
COPY --from=builder /app/frontend/dist /usr/share/ngnix/html

# Copy custom Ngnix configuration
COPY frontend/ngnix.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["ngnix", "-g", "daemon off;"]
