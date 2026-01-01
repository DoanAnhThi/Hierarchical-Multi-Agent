#!/bin/bash
# Deployment script for Multi-Agent System

set -e

echo "=================================="
echo "Deploying Multi-Agent System"
echo "=================================="

# Variables
APP_DIR="/var/www/multi-agent"
VENV_DIR="$APP_DIR/venv"
BACKEND_DIR="$APP_DIR/be"
FRONTEND_DIR="$APP_DIR/fe"

# Navigate to app directory
cd $APP_DIR

# Pull latest changes (if using git)
if [ -d .git ]; then
    echo "Pulling latest changes from git..."
    git pull origin main
fi

# Activate virtual environment
echo "Activating virtual environment..."
source $VENV_DIR/bin/activate

# Update backend dependencies
echo "Updating backend dependencies..."
cd $BACKEND_DIR
pip install --upgrade pip
pip install -r requirements.txt

# Build frontend
echo "Building frontend..."
cd $FRONTEND_DIR
npm install
npm run build

# Create log directory if it doesn't exist
sudo mkdir -p /var/log/multiagent
sudo chown -R $USER:$USER /var/log/multiagent

# Restart services
echo "Restarting services..."
sudo supervisorctl restart multiagent
sudo systemctl reload nginx

# Check service status
echo ""
echo "Service status:"
sudo supervisorctl status multiagent

# Test endpoints
echo ""
echo "Testing backend health..."
curl -s http://localhost:5000/health | python3 -m json.tool || echo "Health check failed"

echo ""
echo "=================================="
echo "Deployment completed!"
echo "=================================="
echo ""
echo "View logs:"
echo "  Backend: sudo tail -f /var/log/multiagent/error.log"
echo "  Nginx: sudo tail -f /var/log/nginx/multiagent_error.log"
echo "  Supervisor: sudo tail -f /var/log/multiagent/supervisor_output.log"
echo ""
echo "Useful commands:"
echo "  Restart app: sudo supervisorctl restart multiagent"
echo "  Stop app: sudo supervisorctl stop multiagent"
echo "  Start app: sudo supervisorctl start multiagent"
echo "  Reload nginx: sudo systemctl reload nginx"

