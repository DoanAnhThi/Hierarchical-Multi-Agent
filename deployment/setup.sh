#!/bin/bash
# AWS EC2 Setup Script for Hierarchical Multi-Agent System
# Compatible with Amazon Linux 2 or Ubuntu

set -e

echo "=================================="
echo "Multi-Agent System - AWS EC2 Setup"
echo "=================================="

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo "Cannot detect OS"
    exit 1
fi

echo "Detected OS: $OS"

# Update system
echo "Updating system packages..."
if [ "$OS" = "amzn" ] || [ "$OS" = "centos" ]; then
    sudo yum update -y
    sudo yum install -y git wget curl
elif [ "$OS" = "ubuntu" ]; then
    sudo apt-get update
    sudo apt-get upgrade -y
    sudo apt-get install -y git wget curl build-essential
fi

# Install Python 3.11
echo "Installing Python 3.11..."
if [ "$OS" = "amzn" ] || [ "$OS" = "centos" ]; then
    sudo yum install -y python3.11 python3.11-pip python3.11-devel
elif [ "$OS" = "ubuntu" ]; then
    sudo apt-get install -y software-properties-common
    sudo add-apt-repository ppa:deadsnakes/ppa -y
    sudo apt-get update
    sudo apt-get install -y python3.11 python3.11-venv python3.11-dev python3-pip
fi

# Create swap file for t2.micro (1GB RAM)
echo "Setting up swap space..."
if [ ! -f /swapfile ]; then
    sudo fallocate -l 2G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
    echo "Swap created and enabled"
else
    echo "Swap file already exists"
fi

# Install Node.js 18.x
echo "Installing Node.js 18.x..."
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
if [ "$OS" = "amzn" ] || [ "$OS" = "centos" ]; then
    sudo yum install -y nodejs
elif [ "$OS" = "ubuntu" ]; then
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

node --version
npm --version

# Install Nginx
echo "Installing Nginx..."
if [ "$OS" = "amzn" ] || [ "$OS" = "centos" ]; then
    sudo amazon-linux-extras install nginx1 -y || sudo yum install -y nginx
elif [ "$OS" = "ubuntu" ]; then
    sudo apt-get install -y nginx
fi

# Install Supervisor
echo "Installing Supervisor..."
if [ "$OS" = "amzn" ] || [ "$OS" = "centos" ]; then
    sudo yum install -y supervisor || sudo pip3 install supervisor
elif [ "$OS" = "ubuntu" ]; then
    sudo apt-get install -y supervisor
fi

# Create application directory
echo "Creating application directory..."
sudo mkdir -p /var/www/multi-agent
sudo chown -R $USER:$USER /var/www/multi-agent

# Clone or setup project
cd /var/www/multi-agent

# Setup Python virtual environment
echo "Setting up Python virtual environment..."
python3.11 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
if [ -f requirements.txt ]; then
    pip install -r requirements.txt
fi

# Copy Nginx configuration
echo "Configuring Nginx..."
sudo cp /var/www/multi-agent/deployment/nginx.conf /etc/nginx/conf.d/multiagent.conf
sudo nginx -t

# Copy Supervisor configuration
echo "Configuring Supervisor..."
sudo cp /var/www/multi-agent/deployment/supervisor.conf /etc/supervisor/conf.d/multiagent.conf

# Start services
echo "Starting services..."
if [ "$OS" = "amzn" ] || [ "$OS" = "centos" ]; then
    sudo systemctl enable nginx
    sudo systemctl start nginx
    sudo systemctl enable supervisord
    sudo systemctl start supervisord
elif [ "$OS" = "ubuntu" ]; then
    sudo systemctl enable nginx
    sudo systemctl start nginx
    sudo systemctl enable supervisor
    sudo systemctl start supervisor
fi

# Reload supervisor
sudo supervisorctl reread
sudo supervisorctl update

# Setup firewall (if UFW is available)
if command -v ufw &> /dev/null; then
    echo "Configuring firewall..."
    sudo ufw allow 22
    sudo ufw allow 80
    sudo ufw allow 443
    sudo ufw --force enable
fi

echo "=================================="
echo "Setup completed successfully!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Copy your .env file to /var/www/multi-agent/backend/.env"
echo "2. Build the frontend: cd frontend && npm install && npm run build"
echo "3. Start the application: sudo supervisorctl start multiagent"
echo "4. Check status: sudo supervisorctl status"
echo "5. View logs: sudo tail -f /var/log/multiagent/*.log"
echo ""
echo "Access your application at: http://YOUR_EC2_PUBLIC_IP"

