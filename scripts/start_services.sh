#!/bin/bash
# scripts/start_services.sh
# Start all services with Docker Compose

set -e

echo "Starting TwinFlow AI services..."

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '#' | xargs)
fi

# Start databases
docker-compose -f docker/docker-compose.yml up -d mongodb redis

# Wait for databases to be ready
echo "Waiting for databases..."
sleep 5

# Start backend and AI services
docker-compose -f docker/docker-compose.yml up -d backend ai simulation

# Start frontend
docker-compose -f docker/docker-compose.yml up -d frontend

echo "All services started."
echo "Frontend: http://localhost:80"
echo "Backend API: http://localhost:8000/api/docs"
echo "n8n: http://localhost:5678"