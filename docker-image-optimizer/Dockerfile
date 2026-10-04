# syntax=docker/dockerfile:1
# ---------------------------------------------------------------
# OPTIMIZED multi-stage Dockerfile
# ---------------------------------------------------------------

# ---------- Stage 1: install deps + run tests ----------
FROM node:22-alpine AS build
WORKDIR /app

# Copy only the manifests first so this layer is cached until
# dependencies actually change
COPY app/package*.json ./
RUN npm install

COPY app/ .
# Fail the build if tests fail
RUN npm test

# ---------- Stage 2: production-only dependencies ----------
FROM node:22-alpine AS deps
WORKDIR /app
COPY app/package*.json ./
RUN npm install --omit=dev && npm cache clean --force

# ---------- Stage 3: minimal runtime ----------
FROM node:22-alpine AS runtime
ENV NODE_ENV=production
WORKDIR /app

# Only production node_modules + the app code. No tests, no dev deps.
COPY --from=deps --chown=node:node /app/node_modules ./node_modules
COPY --from=build --chown=node:node /app/server.js /app/package.json ./

# Built-in non-root user from the official image
USER node

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -qO- http://localhost:3000/health || exit 1

# Run node directly (not via npm) so signals like SIGTERM reach the app
CMD ["node", "server.js"]
