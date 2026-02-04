#!/bin/bash

###############################################################################
# EC2 Initial Setup Script untuk Chin Hin Backend
# 
# Run this script pada fresh EC2 instance untuk install semua dependencies:
# - Docker & Docker Compose
# - Cloudflare Tunnel (cloudflared)
# - Firewall configuration
# - Auto-start services
#
# Usage: sudo bash ec2-setup.sh
###############################################################################

set -e  # Exit on error

echo "🚀 Starting EC2 Setup..."

# Update system packages
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install essential tools
echo "🔧 Installing essential tools..."
sudo apt install -y \
    git \
    curl \
    wget \
    unzip \
    htop \
    vim \
    ufw

# Install Docker
echo "🐳 Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo "✅ Docker installed!"
else
    echo "✅ Docker already installed"
fi

# Install Docker Compose
echo "🐳 Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
        -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose installed!"
else
    echo "✅ Docker Compose already installed"
fi

# Install Cloudflare Tunnel
echo "☁️ Installing Cloudflare Tunnel (cloudflared)..."
if ! command -v cloudflared &> /dev/null; then
    wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
    sudo dpkg -i cloudflared-linux-amd64.deb
    rm cloudflared-linux-amd64.deb
    echo "✅ Cloudflared installed!"
else
    echo "✅ Cloudflared already installed"
fi

# Configure Firewall (UFW) - Only allow SSH
echo "🔒 Configuring firewall..."
sudo ufw --force enable
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
echo "✅ Firewall configured (SSH only - Cloudflare Tunnel handles HTTP/HTTPS)"

# Enable Docker to start on boot
echo "🔄 Enabling Docker auto-start..."
sudo systemctl enable docker
sudo systemctl start docker

# Create application directory
echo "📁 Creating app directory..."
mkdir -p ~/chin-hin-backend
cd ~/chin-hin-backend

echo ""
echo "✅ =============================================="
echo "✅ EC2 Setup Complete!"
echo "✅ =============================================="
echo ""
echo "📋 Next Steps:"
echo "   1. Clone your repository:"
echo "      git clone <your-repo-url> ~/chin-hin-backend"
echo ""
echo "   2. Setup Cloudflare Tunnel:"
echo "      cloudflared tunnel login"
echo "      cloudflared tunnel create chin-hin-backend"
echo ""
echo "   3. Configure environment variables:"
echo "      cp .env.example .env"
echo "      nano .env  # Add your API keys"
echo ""
echo "   4. Deploy application:"
echo "      bash deployment/deploy.sh"
echo ""
echo "💡 Tip: Logout dan login balik untuk Docker group takes effect"
echo "   (or run: newgrp docker)"
