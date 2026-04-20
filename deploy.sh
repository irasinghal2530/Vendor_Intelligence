#!/bin/bash

# Exit on error
set -e

# Configuration
PROJECT_DIR="/home/ubuntu/CostOptimization"
ENV_FILE=".env"
GITHUB_OWNER="irasinghal2530" # Update if needed

# 1. Update the code
echo "🚀 Updating code from repository..."
if [ -d "$PROJECT_DIR" ]; then
    cd "$PROJECT_DIR"
    git pull origin main
else
    git clone https://github.com/$GITHUB_OWNER/CostOptimization.git "$PROJECT_DIR"
    cd "$PROJECT_DIR"
fi

# 2. Check for .env file
if [ ! -f "$ENV_FILE" ]; then
    echo "⚠️ Warning: .env file not found. Please create it with necessary API keys."
    echo "Required: GEMINI_API_KEY"
    echo "Optional: PORT, BACKEND_URL"
    # Create a template if it doesn't exist
    echo "GEMINI_API_KEY=" > .env.template
    echo "PORT=8000" >> .env.template
    echo "BACKEND_URL=http://backend:8000" >> .env.template
fi

# 3. Pull latest images and restart containers
echo "🔄 Restarting services..."
docker compose down
docker compose pull
docker compose up -d --build

echo "✅ Deployment completed successfully!"
echo "Backend: http://<VM_IP>:8000"
echo "Frontend: http://<VM_IP>:8501"
