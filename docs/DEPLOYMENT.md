# 🚀 Chin Hin Deployment Guide - Microsoft Foundry

> **Platform**: Azure AI Foundry (Microsoft Foundry)
> **Target**: Container Apps + Foundry Agent Service

---

## 📋 Prerequisites

- Azure subscription with AI Foundry access
- Azure CLI installed (`az login`)
- Docker installed
- Supabase project (already configured)

---

## 🔧 Environment Variables

Create these in Azure Key Vault or Container Apps secrets:

```env
# Required
SUPABASE_URL=https://nlerjwllnvrpfujuxjnp.supabase.co
SUPABASE_KEY=<your-service-role-key>
GEMINI_API_KEY=<your-gemini-api-key>

# Optional
ENVIRONMENT=production
LOG_LEVEL=INFO
APP_NAME=Chin Hin Employee AI
```

---

## 🐳 Docker Deployment

### Build Image
```bash
cd backend
docker build -t chinhin-backend:latest .
```

### Test Locally
```bash
docker run -p 8000:8000 \
  -e SUPABASE_URL=<url> \
  -e SUPABASE_KEY=<key> \
  -e GEMINI_API_KEY=<key> \
  chinhin-backend:latest
```

---

## ☁️ Azure Container Apps

### 1. Create Resource Group
```bash
az group create --name rg-chinhin --location southeastasia
```

### 2. Create Container App Environment
```bash
az containerapp env create \
  --name env-chinhin \
  --resource-group rg-chinhin \
  --location southeastasia
```

### 3. Deploy Container
```bash
az containerapp create \
  --name chinhin-api \
  --resource-group rg-chinhin \
  --environment env-chinhin \
  --image <your-acr>.azurecr.io/chinhin-backend:latest \
  --target-port 8000 \
  --ingress external \
  --cpu 0.5 \
  --memory 1.0Gi \
  --min-replicas 0 \
  --max-replicas 3 \
  --secrets supabase-url=<url> supabase-key=<key> gemini-key=<key> \
  --env-vars SUPABASE_URL=secretref:supabase-url SUPABASE_KEY=secretref:supabase-key GEMINI_API_KEY=secretref:gemini-key
```

---

## 🤖 Azure AI Foundry (Agent Service)

### For AI Agent Deployment

1. **Go to Azure AI Foundry Portal**
2. **Create AI Hub** in your resource group
3. **Deploy as Foundry Agent**:
   - Use container image as backend
   - Configure agent with system prompt
   - Enable persistent memory
   - Set up enterprise governance

### Foundry Agent Config (Optional)
```yaml
# foundry-agent.yaml
name: chinhin-assistant
description: Chin Hin Employee AI Assistant
runtime:
  type: container
  image: <acr>/chinhin-backend:latest
  port: 8000
capabilities:
  - leave_management
  - room_booking
  - expense_claims
  - proactive_nudges
memory:
  type: persistent
  provider: supabase
```

---

## 🔐 Security Checklist

- [x] RLS enabled on all Supabase tables
- [x] JWT authentication required
- [x] Rate limiting (100 req/min)
- [x] Security headers configured
- [ ] Azure Key Vault for secrets
- [ ] HTTPS only (auto via Container Apps)

---

## 📊 Health Check

```
GET /health
Expected: {"status": "healthy", ...}
```

---

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| 401 Unauthorized | Check SUPABASE_KEY is service_role key |
| AI not responding | Verify GEMINI_API_KEY |
| DB connection failed | Check SUPABASE_URL |

---

*Last Updated: 1 Feb 2026*
