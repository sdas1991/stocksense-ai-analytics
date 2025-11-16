#!/bin/bash

# StockSense AI - Development Mode Runner
# Usage: ./run-dev.sh

echo "🚀 Starting StockSense AI in DEVELOPMENT mode..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker first."
    exit 1
fi

# Stop any running containers
echo "📦 Stopping any existing containers..."
docker-compose -f docker-compose.dev.yml down

# Remove old volumes (optional - comment out if you want to preserve data)
# docker volume rm stocksense-ai-analytics_postgres_dev_data stocksense-ai-analytics_redis_dev_data 2>/dev/null || true

echo ""
echo "🏗️  Building and starting services..."
echo "   - PostgreSQL Database (dev)"
echo "   - Redis Cache"
echo "   - FastAPI Backend (hot reload enabled)"
echo "   - Vue.js Frontend (hot reload enabled)"
echo ""

# Build and start services
docker-compose -f docker-compose.dev.yml up --build

# Cleanup on exit
trap 'echo ""; echo "🛑 Shutting down..."; docker-compose -f docker-compose.dev.yml down' EXIT
