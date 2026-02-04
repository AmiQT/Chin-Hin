#!/bin/bash

###############################################################################
# Deployment Script untuk Chin Hin Backend
# 
# Automates:
# - Git pull latest code
# - Docker build
# - Container restart
# - Health check
#
# Usage: bash deployment/deploy.sh
###############################################################################

set -e  # Exit on error

echo "🚀 Starting Deployment..."
START_TIME=$(date +%s)

# Navigate to project directory
cd ~/chin-hin-backend || cd "$(dirname "$0")/.."

# Pull latest code (if using git)
if [ -d ".git" ]; then
    echo "📥 Pulling latest code from Git..."
    git pull origin main || git pull origin master
else
    echo "⚠️  Not a git repository, skipping git pull"
fi

# Stop and remove existing containers
echo "🛑 Stopping existing containers..."
docker-compose down || true

# Build Docker image
echo "🐳 Building Docker image..."
docker-compose build --no-cache

# Start containers in detached mode
echo "▶️  Starting containers..."
docker-compose up -d

# Wait for container to be ready
echo "⏳ Waiting for application to be ready..."
sleep 10

# Health check
echo "🏥 Running health check..."
MAX_RETRIES=10
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -sf http://localhost:8000/health > /dev/null; then
        echo "✅ Health check passed!"
        break
    else
        RETRY_COUNT=$((RETRY_COUNT + 1))
        if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
            echo "❌ Health check failed after $MAX_RETRIES attempts"
            echo "📋 Container logs:"
            docker-compose logs --tail=50
            exit 1
        fi
        echo "⏳ Attempt $RETRY_COUNT/$MAX_RETRIES failed, retrying in 5s..."
        sleep 5
    fi
done

# Show container status
echo "📊 Container status:"
docker-compose ps

# Calculate deployment time
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo ""
echo "✅ =============================================="
echo "✅ Deployment Successful! 🎉"
echo "✅ =============================================="
echo "   Time taken: ${DURATION}s"
echo ""
echo "📋 Quick Commands:"
echo "   View logs:     docker-compose logs -f"
echo "   Restart:       docker-compose restart"
echo "   Stop:          docker-compose down"
echo "   Shell access:  docker-compose exec backend bash"
echo ""
echo "🌐 Access your API:"
echo "   Local:  http://localhost:8000"
echo "   Docs:   http://localhost:8000/docs"
echo "   Health: http://localhost:8000/health"
