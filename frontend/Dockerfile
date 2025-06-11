# Production Dockerfile for NSAI Orchestrator Frontend
# Multi-stage build for optimal image size

# Build stage
FROM node:18-alpine as builder

# Set build arguments
ARG BUILD_DATE
ARG VERSION
ARG VCS_REF
ARG NEXT_PUBLIC_API_URL

# Add labels
LABEL org.opencontainers.image.title="NSAI Orchestrator MCP Frontend" \
      org.opencontainers.image.description="Production-grade frontend for multi-agent orchestration platform" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.revision="${VCS_REF}" \
      org.opencontainers.image.vendor="NSAI Team" \
      org.opencontainers.image.licenses="MIT"

# Install dependencies for building
RUN apk add --no-cache libc6-compat git

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY tsconfig.json ./
COPY next.config.js* ./
COPY tailwind.config.js ./
COPY postcss.config.js ./

# Install dependencies
RUN npm ci --only=production --ignore-scripts && npm cache clean --force

# Copy source code
COPY . .

# Set environment variables for build
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}

# Build application
RUN npm run build

# Production stage
FROM node:18-alpine as production

# Set build arguments
ARG BUILD_DATE
ARG VERSION
ARG VCS_REF

# Add labels
LABEL org.opencontainers.image.title="NSAI Orchestrator MCP Frontend" \
      org.opencontainers.image.description="Production-grade frontend for multi-agent orchestration platform" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.revision="${VCS_REF}" \
      org.opencontainers.image.vendor="NSAI Team" \
      org.opencontainers.image.licenses="MIT"

# Install runtime dependencies
RUN apk add --no-cache curl && \
    addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

WORKDIR /app

# Copy built application from builder stage
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/public ./public

# Set environment variables
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Security: Don't run as root
USER nextjs

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/api/health || exit 1

# Expose port
EXPOSE 3000

# Start command
CMD ["node", "server.js"]