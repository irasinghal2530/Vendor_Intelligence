#!/bin/bash

# Exit on error
set -e

echo "🔧 Preparing Oracle VM for deployment..."

# 1. Update system packages
sudo apt update && sudo apt upgrade -y

# 2. Install Git
sudo apt install -y git

# 3. Install Docker
if ! command -v docker &> /dev/null; then
    echo "🐳 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    # New group membership doesn't take effect in the current shell
else
    echo "✅ Docker already installed."
fi

# 4. Install Docker Compose
if ! docker compose version &> /dev/null; then
    echo "🐳 Installing Docker Compose..."
    # The 'docker-compose-plugin' is usually the best approach for Ubuntu modern images
    sudo apt-get install docker-compose-plugin -y
else
    echo "✅ Docker Compose already installed."
fi

# 5. Open necessary ports (UFW)
# Oracle VM usually has a security list in the cloud UI, 
# but we should also open them in the local firewall.
echo "🔓 Opening ports 8000 (Backend) and 8501 (Frontend)..."
sudo ufw allow 8000/tcp
sudo ufw allow 8501/tcp
# sudo ufw enable --force # Warning: disabling this as it might lock users out of SSH.

echo "✅ System preparation completed!"
echo "⚠️ IMPORTANT: Please logout and login again to apply Docker user group changes."
echo "Then, run: chmod +x deploy.sh && ./deploy.sh"
