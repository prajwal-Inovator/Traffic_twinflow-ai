#!/bin/bash
# scripts/deploy.sh
# Deploy to production using Docker Compose (or Render CLI)

set -e

echo "🚀 Starting deployment..."

# Load production environment variables
if [ -f .env.production ]; then
    export $(grep -v '^#' .env.production | xargs)
else
    echo "❌ .env.production not found!"
    exit 1
fi

# Pull latest code (if using git)
git pull origin main

# Build and run with Docker Compose production
docker-compose -f docker/docker-compose.prod.yml pull
docker-compose -f docker/docker-compose.prod.yml up -d --build

# Run database migrations (if any)
docker-compose -f docker/docker-compose.prod.yml exec backend python -m app.migrations.upgrade

echo "✅ Deployment complete!"
echo "Check services: docker-compose -f docker/docker-compose.prod.yml ps"