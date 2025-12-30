# AWS Free Tier Deployment Guide

## Prerequisites

- AWS Account with Free Tier eligibility
- Basic knowledge of AWS EC2 and SSH
- OpenAI API Key
- (Optional) Tavily API Key for enhanced web search

## Step 1: Launch EC2 Instance

### Instance Configuration

1. **Go to EC2 Dashboard** → Click "Launch Instance"

2. **Name**: `multi-agent-system`

3. **AMI Selection**:
   - Choose: **Amazon Linux 2023** or **Ubuntu Server 22.04 LTS**
   - Both are Free Tier eligible

4. **Instance Type**:
   - Select: **t2.micro** (1 vCPU, 1GB RAM)
   - Free Tier: 750 hours/month

5. **Key Pair**:
   - Create new or use existing key pair
   - Download and save `.pem` file securely
   - Set permissions: `chmod 400 your-key.pem`

6. **Network Settings**:
   - Create security group or use existing
   - Allow these inbound rules:
     - SSH (22) from your IP
     - HTTP (80) from anywhere (0.0.0.0/0)
     - HTTPS (443) from anywhere (0.0.0.0/0)

7. **Storage**:
   - 30 GB gp3 (Free Tier eligible)

8. **Launch Instance**

## Step 2: Connect to EC2

```bash
# SSH into your instance
ssh -i your-key.pem ec2-user@YOUR_EC2_PUBLIC_IP

# For Ubuntu:
ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

## Step 3: Upload Project Files

### Option A: Using Git (Recommended)

```bash
# On your local machine, push to GitHub
cd "/Users/MAC/Documents/0. Javis/Hierarchical Multi-Agent"
git init
git add .
git commit -m "Initial commit"
git remote add origin YOUR_GITHUB_REPO
git push -u origin main

# On EC2 instance
cd /var/www
sudo mkdir -p multi-agent
sudo chown -R $USER:$USER multi-agent
cd multi-agent
git clone YOUR_GITHUB_REPO .
```

### Option B: Using SCP

```bash
# From your local machine
cd "/Users/MAC/Documents/0. Javis/Hierarchical Multi-Agent"
scp -i your-key.pem -r * ec2-user@YOUR_EC2_PUBLIC_IP:/tmp/multi-agent/

# On EC2, move files
ssh -i your-key.pem ec2-user@YOUR_EC2_PUBLIC_IP
sudo mkdir -p /var/www/multi-agent
sudo cp -r /tmp/multi-agent/* /var/www/multi-agent/
sudo chown -R $USER:$USER /var/www/multi-agent
```

## Step 4: Run Setup Script

```bash
cd /var/www/multi-agent
chmod +x deployment/setup.sh
./deployment/setup.sh
```

This script will:
- Install Python 3.11
- Install Node.js 18.x
- Install Nginx
- Install Supervisor
- Create swap file (important for t2.micro)
- Configure system

## Step 5: Configure Environment Variables

```bash
cd /var/www/multi-agent/backend
cp .env.example .env
nano .env
```

Update with your keys:

```bash
OPENAI_API_KEY=your_actual_openai_key
TAVILY_API_KEY=your_actual_tavily_key
FLASK_ENV=production
FLASK_SECRET_KEY=generate_random_secret_here
```

Generate secret key:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

## Step 6: Install Dependencies

```bash
# Backend
cd /var/www/multi-agent/backend
source ../venv/bin/activate
pip install -r requirements.txt

# Frontend
cd /var/www/multi-agent/frontend
npm install
npm run build
```

## Step 7: Create Log Directory

```bash
sudo mkdir -p /var/log/multiagent
sudo chown -R $USER:$USER /var/log/multiagent
```

## Step 8: Start Services

```bash
# Start backend with Supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start multiagent

# Start Nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Check status
sudo supervisorctl status
sudo systemctl status nginx
```

## Step 9: Test Deployment

```bash
# Test backend health
curl http://localhost:5000/health

# Test from browser
# Open: http://YOUR_EC2_PUBLIC_IP
```

## Step 10: (Optional) Setup Domain and SSL

### If you have a domain:

1. **Point domain to EC2**:
   - Add A record: `your-domain.com` → EC2 Public IP
   - Wait for DNS propagation (5-30 minutes)

2. **Setup SSL**:
```bash
cd /var/www/multi-agent/deployment
chmod +x ssl-setup.sh
./ssl-setup.sh your-domain.com
```

3. **Update Nginx configuration**:
   - Uncomment SSL block in `/etc/nginx/conf.d/multiagent.conf`
   - Update `server_name` with your domain
   - Reload: `sudo systemctl reload nginx`

## Cost Optimization for Free Tier

### Monthly Free Tier Limits:
- **EC2**: 750 hours t2.micro (enough for 1 instance 24/7)
- **Storage**: 30GB EBS gp3
- **Data Transfer**: 15GB outbound
- **Elastic IP**: 1 free (when attached to running instance)

### Tips to Stay Within Free Tier:

1. **Monitor Usage**:
   - AWS Console → Billing → Free Tier Usage
   - Set up billing alerts

2. **Optimize Memory**:
   - Swap file is configured (2GB)
   - Gunicorn workers set to 4 (tuned for 1GB RAM)

3. **Stop Instance When Not Testing**:
   ```bash
   # Stop instance (doesn't use hours)
   aws ec2 stop-instances --instance-ids YOUR_INSTANCE_ID
   
   # Start when needed
   aws ec2 start-instances --instance-ids YOUR_INSTANCE_ID
   ```

4. **CloudWatch Monitoring**:
   - Basic monitoring is free
   - Monitor CPU, memory, and network usage

## Troubleshooting

### Service won't start:
```bash
# Check logs
sudo tail -f /var/log/multiagent/error.log
sudo tail -f /var/log/nginx/multiagent_error.log

# Restart services
sudo supervisorctl restart multiagent
sudo systemctl restart nginx
```

### Out of memory:
```bash
# Check swap
free -h

# Increase swap if needed
sudo fallocate -l 4G /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Can't access from browser:
```bash
# Check security group allows HTTP (80)
# Check Nginx is running
sudo systemctl status nginx

# Check if port is listening
sudo netstat -tlnp | grep :80
```

### SSL issues:
```bash
# Check certificate
sudo certbot certificates

# Renew manually
sudo certbot renew

# Check Nginx config
sudo nginx -t
```

## Monitoring and Maintenance

### View Logs:
```bash
# Application logs
sudo tail -f /var/log/multiagent/error.log

# Nginx logs
sudo tail -f /var/log/nginx/multiagent_error.log

# Supervisor logs
sudo tail -f /var/log/multiagent/supervisor_output.log
```

### Update Application:
```bash
cd /var/www/multi-agent
chmod +x deployment/deploy.sh
./deployment/deploy.sh
```

### Backup:
```bash
# Create snapshot of EBS volume in AWS Console
# Backup .env file locally
scp -i your-key.pem ec2-user@YOUR_IP:/var/www/multi-agent/backend/.env ./backup.env
```

## Security Best Practices

1. **Keep SSH key secure** - Never commit to git
2. **Update security group** - Limit SSH to your IP only
3. **Regular updates**:
   ```bash
   sudo yum update -y  # Amazon Linux
   sudo apt update && sudo apt upgrade -y  # Ubuntu
   ```
4. **Use IAM roles** - Don't hardcode AWS credentials
5. **Enable CloudWatch alarms** - Monitor unusual activity
6. **Rotate API keys** - Change periodically

## Next Steps

1. Set up CI/CD pipeline (GitHub Actions)
2. Configure CloudWatch alarms
3. Add Redis for caching (optional)
4. Scale to multiple instances (load balancer)
5. Use RDS for database (if adding persistence)

## Support

For issues:
- Check logs first
- Review security group settings
- Verify .env configuration
- Check AWS Free Tier usage

