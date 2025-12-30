#!/bin/bash
# SSL Setup using Let's Encrypt (Certbot)

set -e

echo "=================================="
echo "SSL Certificate Setup"
echo "=================================="

# Check if domain is provided
if [ -z "$1" ]; then
    echo "Usage: ./ssl-setup.sh your-domain.com"
    exit 1
fi

DOMAIN=$1
EMAIL="admin@$DOMAIN"  # Change this to your email

echo "Setting up SSL for domain: $DOMAIN"

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
fi

# Install Certbot
echo "Installing Certbot..."
if [ "$OS" = "amzn" ] || [ "$OS" = "centos" ]; then
    sudo yum install -y certbot python3-certbot-nginx
elif [ "$OS" = "ubuntu" ]; then
    sudo apt-get install -y certbot python3-certbot-nginx
fi

# Stop Nginx temporarily
sudo systemctl stop nginx

# Obtain certificate
echo "Obtaining SSL certificate..."
sudo certbot certonly --standalone \
    --non-interactive \
    --agree-tos \
    --email $EMAIL \
    -d $DOMAIN

# Update Nginx configuration
echo "Updating Nginx configuration..."
sudo sed -i "s/server_name _;/server_name $DOMAIN;/" /etc/nginx/conf.d/multiagent.conf

# Restart Nginx
sudo systemctl start nginx

# Test SSL renewal
echo "Testing SSL renewal..."
sudo certbot renew --dry-run

# Setup auto-renewal
echo "Setting up auto-renewal..."
(crontab -l 2>/dev/null; echo "0 3 * * * /usr/bin/certbot renew --quiet --post-hook 'systemctl reload nginx'") | crontab -

echo ""
echo "=================================="
echo "SSL setup completed!"
echo "=================================="
echo "Your site is now accessible at: https://$DOMAIN"
echo "Certificate will auto-renew every 90 days"

