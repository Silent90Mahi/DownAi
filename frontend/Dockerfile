# ============================================================================
# Ooumph Frontend Dockerfile
# React + Vite + Node 20
# ============================================================================

ARG NODE_VERSION=20

# ============================================================================
# Stage 1: Base Image
# ============================================================================
FROM node:${NODE_VERSION}-alpine as base

# Set work directory
WORKDIR /app

# ============================================================================
# Stage 2: Dependencies
# ============================================================================
FROM base as dependencies

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm ci

# ============================================================================
# Stage 3: Development
# ============================================================================
FROM base as development

# Copy dependencies from previous stage
COPY --from=dependencies /app/node_modules ./node_modules

# Copy application code
COPY . .

# Expose port
EXPOSE 5173

# Run development server with hot reload
CMD ["npm", "run", "dev", "--", "--host"]

# ============================================================================
# Stage 4: Production Build
# ============================================================================
FROM base as build

# Copy dependencies from previous stage
COPY --from=dependencies /app/node_modules ./node_modules

# Copy application code
COPY . .

ARG VITE_API_BASE_URL=http://localhost:6002
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

# Build the application
RUN npm run build

# ============================================================================
# Stage 5: Production Serve
# ============================================================================
FROM nginx:alpine as production

# Copy built files from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
