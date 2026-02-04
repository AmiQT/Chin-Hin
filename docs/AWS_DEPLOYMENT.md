# AWS EC2 Deployment Guide - Chin Hin Backend 🚀

Complete step-by-step guide untuk deploy FastAPI backend ke AWS EC2 dengan Cloudflare Tunnel.

---

## 📋 Table of Contents

1. [Pre-requisites](#pre-requisites)
2. [EC2 Instance Setup](#ec2-instance-setup)
3. [Initial Server Configuration](#initial-server-configuration)
4. [Cloudflare Tunnel Setup](#cloudflare-tunnel-setup)
5. [Application Deployment](#application-deployment)
6. [Domain Configuration](#domain-configuration)
7. [Maintenance & Updates](#maintenance--updates)
8. [Troubleshooting](#troubleshooting)
9. [Cost Monitoring](#cost-monitoring)

---

## Pre-requisites

Sebelum start, pastikan ada:

- ✅ **AWS Account** dengan active credits
- ✅ **Cloudflare Account** (free tier okay!)
- ✅ **SSH Key Pair** untuk EC2 access
- ✅ **Git Repository** dengan backend code
- ✅ **Supabase Account** dengan database setup
- ✅ **Gemini API Key** dari Google AI Studio

---

## EC2 Instance Setup

### Step 1: Launch EC2 Instance

1. **Login to AWS Console** → EC2 Dashboard

2. **Click "Launch Instance"**

3. **Configure Instance:**
   ```
   Name: chin-hin-backend
   
   AMI: Ubuntu Server 22.04 LTS (HVM), SSD Volume Type
   
   Instance Type: t3.small
   - 2 vCPU
   - 2 GiB RAM
   - Cost: ~$0.0208/hour (~$15/month)
   
   Key Pair: Select your SSH key (atau create new)
   
   Network Settings:
   - Create security group
   - Allow SSH (port 22) from My IP
   - NO NEED port 80/443 (Cloudflare Tunnel handles this!)
   
   Storage: 8 GiB gp3 (default okay)
   ```

4. **Click "Launch Instance"** 🚀

5. **Wait 2-3 minutes** untuk instance ready

6. **Note down Public IP** - You'll need this untuk SSH

### Step 2: Connect to EC2

```bash
# Windows (PowerShell)
ssh -i "path/to/your-key.pem" ubuntu@<EC2_PUBLIC_IP>

# macOS/Linux
chmod 400 your-key.pem
ssh -i your-key.pem ubuntu@<EC2_PUBLIC_IP>
```

Kalau connection successful, you'll see Ubuntu welcome screen! 🎉

---

## Initial Server Configuration

### Step 3: Run Setup Script

Copy setup script ke server dan run:

```bash
# Download setup script
wget https://raw.githubusercontent.com/<your-repo>/backend/deployment/ec2-setup.sh

# Make executable
chmod +x ec2-setup.sh

# Run setup (password needed untuk sudo)
sudo bash ec2-setup.sh
```

Script akan install:
- ✅ Docker & Docker Compose
- ✅ Cloudflare Tunnel (cloudflared)
- ✅ Essential tools (git, curl, etc)
- ✅ Firewall configuration

**Ini takes 5-10 minit.** Lepas habis, **logout dan login balik** untuk Docker group changes.

```bash
# Logout
exit

# Login balik
ssh -i your-key.pem ubuntu@<EC2_PUBLIC_IP>

# Verify Docker works without sudo
docker ps
```

---

## Cloudflare Tunnel Setup

### Step 4: Create Cloudflare Tunnel

1. **Login to Cloudflare:**
   ```bash
   cloudflared tunnel login
   ```
   
   - Browser akan bukak untuk authenticate
   - Select your domain (kalau takde, create free subdomain)
   - Authorize access

2. **Create Tunnel:**
   ```bash
   cloudflared tunnel create chin-hin-backend
   ```
   
   - Akan dapat **Tunnel ID** - copy this!
   - Credentials file auto-created: `~/.cloudflared/<TUNNEL_ID>.json`

3. **Configure Tunnel:**
   
   Download tunnel config dari repo:
   ```bash
cd ~
git clone <your-repo-url> chin-hin-backend
   cd chin-hin-backend/backend/deployment
   
   # Edit config file
   nano cloudflare-tunnel.yml
   ```
   
   Update dengan your tunnel ID:
   ```yaml
   tunnel: <YOUR_TUNNEL_ID>  # Paste your tunnel ID here
   credentials-file: /home/ubuntu/.cloudflared/<YOUR_TUNNEL_ID>.json
   
   ingress:
     - hostname: api.yourdomain.com  # Update dengan your subdomain
       service: http://localhost:8000
       originRequest:
         noTLSVerify: true
         connectTimeout: 30s
         keepAliveConnections: 10
     - service: http_status:404
   ```

4. **Copy Config to Cloudflare Directory:**
   ```bash
   sudo mkdir -p /etc/cloudflared
   sudo cp cloudflare-tunnel.yml /etc/cloudflared/config.yml
   ```

5. **Install as System Service:**
   ```bash
   sudo cloudflared service install
   sudo systemctl start cloudflared
   sudo systemctl enable cloudflared
   ```

6. **Verify Tunnel Running:**
   ```bash
   sudo systemctl status cloudflared
   # Should show "active (running)"
   ```

---

## Application Deployment

### Step 5: Setup Environment Variables

```bash
cd ~/chin-hin-backend/backend

# Copy environment template
cp .env.production.template .env

# Edit with your actual values
nano .env
```

Update these values:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-actual-key
GEMINI_API_KEY=your-actual-key
ALLOWED_ORIGINS=https://api.yourdomain.com
```

**Save:** `Ctrl+X` → `Y` → `Enter`

### Step 6: Deploy Application

```bash
# Make deploy script executable
chmod +x deployment/deploy.sh

# Run deployment
bash deployment/deploy.sh
```

Script akan:
1. Build Docker image
2. Start container
3. Run health checks
4. Show status

Kalau successful, you'll see:
```
✅ Deployment Successful! 🎉
```

### Step 7: Verify Deployment

```bash
# Test locally
curl http://localhost:8000/health

# Should return: {"status":"healthy"}

# Check container logs
docker-compose logs -f

# Ctrl+C to exit logs
```

---

## Domain Configuration

### Step 8: Configure DNS in Cloudflare

1. **Login to Cloudflare Dashboard**

2. **Go to:** Zero Trust → Access → Tunnels

3. **Find your tunnel:** `chin-hin-backend`

4. **Click "Configure"**

5. **Public Hostname Tab:**
   - Click "+ Add a public hostname"
   - **Subdomain:** `api` (atau apa-apa you nak)
   - **Domain:** Select your domain
   - **Service:** `http://localhost:8000`
   - **Save**

6. **Test DNS:**
   ```bash
   # Wait 1-2 minutes untuk DNS propagate
   curl https://api.yourdomain.com/health
   ```

Kalau dapat response, **CONGRATS!** Your API is live! 🎉

---

## Maintenance & Updates

### Update Code

```bash
cd ~/chin-hin-backend/backend

# Pull latest changes
git pull origin main

# Redeploy
bash deployment/deploy.sh
```

### View Logs

```bash
# All logs
docker-compose logs

# Follow logs (real-time)
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100

# Specific service
docker-compose logs api
```

### Restart Application

```bash
# Restart containers
docker-compose restart

# Stop application
docker-compose down

# Start application
docker-compose up -d
```

### Monitor Resources

```bash
# System resources
htop

# Docker stats
docker stats

# Disk usage
df -h

# Container logs size
docker system df
```

---

## Troubleshooting

### Issue: Container Won't Start

```bash
# Check container logs
docker-compose logs api

# Check for port conflicts
sudo netstat -tulpn | grep 8000

# Rebuild from scratch
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Issue: Health Check Failing

```bash
# Test endpoint manually
curl -v http://localhost:8000/health

# Check if process running
docker-compose ps

# Check environment variables loaded
docker-compose exec api env | grep SUPABASE
```

### Issue: Cloudflare Tunnel Not Working

```bash
# Check tunnel status
sudo systemctl status cloudflared

# View tunnel logs
sudo journalctl -u cloudflared -f

# Restart tunnel
sudo systemctl restart cloudflared

# Test tunnel connectivity
cloudflared tunnel info chin-hin-backend
```

### Issue: Out of Memory

```bash
# Check memory usage
free -h

# Restart container dengan memory limit
docker-compose down
docker-compose up -d

# Clear Docker cache
docker system prune -a
```

### Issue: SSL/Certificate Errors

Cloudflare Tunnel automatically handles HTTPS. Kalau ada issues:

1. Check Cloudflare dashboard → SSL/TLS settings
2. Set to "Full" (NOT "Full (strict)")
3. Wait 5 minutes untuk propagate

---

## Cost Monitoring

### AWS Budgets Setup

1. **AWS Console** → Billing → Budgets

2. **Create Budget:**
   - Type: Cost budget
   - Name: "EC2 Monthly Budget"
   - Budgeted amount: $30.00
   - Alert threshold: 80% ($24)

3. **Email Alerts:** Add your email

### Expected Monthly Costs

```
t3.small Instance:     $15-17/month
EBS Storage (8GB):     $0.80/month
Data Transfer (10GB):  $0.90/month
------------------------
TOTAL:                 ~$17-19/month
```

**Tips untuk save cost:**
- Stop instance bila tak guna (Development/Testing)
- Use AWS Free Tier (12 months free untuk new accounts)
- Reserved Instance (save 30-60% untuk 1-year commit)

### Monitor Usage

```bash
# On EC2 instance
# Check uptime
uptime

# Check network usage
vnstat -d

# Check API requests (from logs)
docker-compose logs api | grep "GET \|POST " | wc -l
```

---

## Quick Reference Commands

```bash
# ======================
# DEPLOYMENT
# ======================
bash deployment/deploy.sh          # Deploy/Update app
docker-compose restart              # Restart app
docker-compose down                 # Stop app
docker-compose up -d                # Start app

# ======================
# MONITORING
# ======================
docker-compose logs -f              # View logs
docker-compose ps                   # Container status
docker stats                        # Resource usage
htop                               # System monitor

# ======================
# CLOUDFLARE TUNNEL
# ======================
sudo systemctl status cloudflared   # Tunnel status
sudo systemctl restart cloudflared  # Restart tunnel
sudo journalctl -u cloudflared -f   # Tunnel logs

# ======================
# MAINTENANCE
# ======================
docker system prune -a             # Clean Docker cache
sudo apt update && sudo apt upgrade # Update system
df -h                              # Disk usage
free -h                            # Memory usage
```

---

## Security Best Practices

1. **✅ Keep System Updated:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **✅ Use Strong Passwords:**
   - Generate long JWT secrets
   - Rotate API keys regularly

3. **✅ Monitor Logs:**
   - Check logs for suspicious activity
   - Setup log rotation

4. **✅ Firewall:**
   - Only SSH port exposed
   - Cloudflare handles HTTP/HTTPS

5. **✅ Backups:**
   - Supabase auto-backup your data
   - Git for code version control

---

## Support & Resources

- **AWS Documentation:** https://docs.aws.amazon.com/ec2/
- **Cloudflare Tunnel Docs:** https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/
- **Docker Compose:** https://docs.docker.com/compose/
- **FastAPI Deployment:** https://fastapi.tiangolo.com/deployment/

---

## Conclusion

You now have:
- ✅ FastAPI backend running on AWS EC2
- ✅ Automatic HTTPS via Cloudflare Tunnel
- ✅ DDoS protection included
- ✅ Auto-deployment scripts
- ✅ Production-ready setup

**Total setup time:** ~30-45 minutes  
**Monthly cost:** ~$17-19 USD

**Next Steps:**
1. Update mobile app dengan new API URL
2. Test all endpoints
3. Setup monitoring alerts
4. Plan Azure migration (bila ready)

Happy deploying! 🚀
