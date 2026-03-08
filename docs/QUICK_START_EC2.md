# Quick Start - EC2 Deployment 🚀

One-page reference untuk deploy backend ke AWS EC2 dengan Cloudflare Tunnel.

---

## 🎯 Prerequisites Checklist

```bash
✅ AWS Account dengan credits ($70++ available)
✅ Cloudflare Account (free tier)
✅ SSH Key untuk EC2
✅ Git repository URL
✅ Azure OpenAI API Key
✅ Gemini API Key
```

---

## ⚡ Quick Deployment (30 minutes)

### 1️⃣ Launch EC2 Instance (5 min)

AWS Console → EC2 → Launch Instance:
- **Name:** chin-hin-backend
- **AMI:** Ubuntu 22.04 LTS
- **Type:** t3.small (2GB RAM / 2vCPU)
- **Security Group:** Allow SSH only
- **Storage:** 8GB gp3

💰 **Cost:** ~$17/month

### 2️⃣ Initial Setup (10 min)

```bash
# SSH into server
ssh -i your-key.pem ubuntu@<EC2_IP>

# Download & run setup
wget https://raw.githubusercontent.com/<repo>/backend/deployment/ec2-setup.sh
chmod +x ec2-setup.sh
sudo bash ec2-setup.sh

# Logout & login untuk Docker group
exit
ssh -i your-key.pem ubuntu@<EC2_IP>
```

### 3️⃣ Cloudflare Tunnel (10 min)

```bash
# Login to Cloudflare
cloudflared tunnel login

# Create tunnel
cloudflared tunnel create chin-hin-backend
# Copy the Tunnel ID!

# Clone repo
git clone <your-repo-url> ~/chin-hin-backend
cd ~/chin-hin-backend/backend/deployment

# Edit tunnel config
nano cloudflare-tunnel.yml
# Update: tunnel ID, hostname, credentials path

# Install service
sudo cp cloudflare-tunnel.yml /etc/cloudflared/config.yml
sudo cloudflared service install
sudo systemctl start cloudflared
```

### 4️⃣ Deploy Application (5 min)

```bash
cd ~/chin-hin-backend/backend

# Setup environment
cp .env.production.template .env
nano .env  # Add your API keys

# Deploy
chmod +x deployment/deploy.sh
bash deployment/deploy.sh
```

### 5️⃣ Configure DNS (2 min)

Cloudflare Dashboard → Zero Trust → Tunnels → Configure:
- Add public hostname: `api.yourdomain.com`
- Service: `http://localhost:8000`

**Test:** `curl https://api.yourdomain.com/health`

---

## 📱 Update Mobile App

Update API base URL in mobile app:

```dart
// lib/services/api_service.dart
static const String baseUrl = 'https://api.yourdomain.com';
```

Rebuild & test! 🎉

---

## 🔄 Daily Commands

```bash
# Update app
cd ~/chin-hin-backend/backend
git pull && bash deployment/deploy.sh

# View logs
docker-compose logs -f

# Restart
docker-compose restart

# Check status
docker-compose ps
sudo systemctl status cloudflared
```

---

## 🆘 Emergency Troubleshooting

**App not responding:**
```bash
docker-compose restart
docker-compose logs --tail=50
```

**Tunnel down:**
```bash
sudo systemctl restart cloudflared
sudo journalctl -u cloudflared -f
```

**Out of memory:**
```bash
docker system prune -a
docker-compose restart
```

---

## 💰 Cost Estimate

| Item | Monthly Cost |
|------|-------------|
| t3.small | $15-17 |
| Storage 8GB | $0.80 |
| Data Transfer | $0.90 |
| **Total** | **~$17-19** |

Your $70 budget = **~4 months runtime** 💸

---

## 📊 Architecture

```
Mobile App
    ↓ HTTPS
Cloudflare Network (DDoS protection, SSL)
    ↓ Encrypted Tunnel
EC2 t3.small (Ubuntu 22.04)
    ↓ Docker
FastAPI Backend (:8000)
    ↓ API Calls
Azure OpenAI
```

---

## ✅ Success Criteria

After deployment, verify:

- [ ] API health check: `https://api.yourdomain.com/health`
- [ ] Swagger docs: `https://api.yourdomain.com/docs`
- [ ] Mobile app connects successfully
- [ ] Cloudflare tunnel status: Active
- [ ] Docker container: Running
- [ ] Logs: No errors

---

## 🎓 Full Documentation

For detailed guide: [AWS_DEPLOYMENT.md](./AWS_DEPLOYMENT.md)

---

**Setup Time:** 30-45 minutes  
**Difficulty:** ⭐⭐⭐ (Intermediate)  
**Scalability:** 5-10 concurrent users  

Happy deploying! 🚀
