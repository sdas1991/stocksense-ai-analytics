#!/bin/bash

# StockSense AI - Production Mode Runner
# Usage: ./run-prod.sh

echo "🚀 Starting StockSense AI in PRODUCTION mode..."
echo ""

# Check if .env.prod exists
if [ ! -f .env.prod ]; then
    echo "❌ Error: .env.prod file not found!"
    echo ""
    echo "Please create .env.prod with the following required variables:"
    echo "  - POSTGRES_PASSWORD"
    echo "  - REDIS_PASSWORD"
    echo "  - SECRET_KEY"
    echo "  - AWS_ACCESS_KEY_ID (if using Bedrock)"
    echo "  - AWS_SECRET_ACCESS_KEY (if using Bedrock)"
    echo ""
    echo "Example:"
    echo "  cp .env.prod.example .env.prod"
    echo "  # Then edit .env.prod with your values"
    exit 1
fi

# Load environment variables
set -a
source .env.prod
set +a

# Check required variables
REQUIRED_VARS=("POSTGRES_PASSWORD" "REDIS_PASSWORD" "SECRET_KEY")
MISSING_VARS=()

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        MISSING_VARS+=("$var")
    fi
done

if [ ${#MISSING_VARS[@]} -ne 0 ]; then
    echo "❌ Error: Missing required environment variables:"
    printf '   - %s\n' "${MISSING_VARS[@]}"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker first."
    exit 1
fi

echo "✅ Environment variables validated"
echo ""
echo "🏗️  Building and starting production services..."
echo "   - PostgreSQL Database (production)"
echo "   - Redis Cache (password protected)"
echo "   - FastAPI Backend (optimized build)"
echo "   - Vue.js Frontend (production build)"
echo "   - Nginx Reverse Proxy"
echo ""

# Build and start in detached mode
docker-compose -f docker-compose.prod.yml up --build -d

echo ""
echo "✅ Production services started successfully!"
echo ""
echo "📊 Service URLs:"
echo "   - Application: http://localhost"
echo "   - API: http://localhost/api"
echo "   - API Docs: http://localhost/docs"
echo ""
echo "📝 Useful commands:"
echo "   - View logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "   - Stop services: docker-compose -f docker-compose.prod.yml down"
echo "   - Restart: docker-compose -f docker-compose.prod.yml restart"
echo ""
