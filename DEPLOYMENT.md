# Deployment Guide - NSAI Orchestrator MCP

This guide covers deploying the NSAI Orchestrator MCP to various platforms, with detailed instructions for Vercel frontend deployment and backend hosting options.

## 🚀 Quick Deploy to Vercel

The fastest way to get the frontend running is to deploy to Vercel:

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fehudso7%2Fnsai-orchestrator-mcp&env=NEXT_PUBLIC_API_URL,NEXT_PUBLIC_WS_URL&envDescription=Required%20environment%20variables%20for%20API%20connection&envLink=https%3A%2F%2Fgithub.com%2Fehudso7%2Fnsai-orchestrator-mcp%23environment-variables)

## 📋 Table of Contents

- [Frontend Deployment (Vercel)](#frontend-deployment-vercel)
- [Backend Deployment Options](#backend-deployment-options)
- [Full Stack Deployment](#full-stack-deployment)
- [Environment Variables](#environment-variables)
- [Post-Deployment Setup](#post-deployment-setup)
- [Troubleshooting](#troubleshooting)

## 🎯 Frontend Deployment (Vercel)

### Prerequisites

1. **GitHub Repository**: Ensure your code is pushed to GitHub
2. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
3. **Backend API**: Have a running backend API (see backend deployment options below)

### Method 1: Deploy via Vercel Dashboard

1. **Connect Repository**
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Click "New Project"
   - Import your GitHub repository: `nsai-orchestrator-mcp`

2. **Configure Build Settings**
   - **Framework Preset**: Next.js
   - **Root Directory**: Leave blank (auto-detected)
   - **Build Command**: `cd frontend && npm run build`
   - **Output Directory**: `frontend/.next`
   - **Install Command**: `cd frontend && npm install`

3. **Set Environment Variables**
   ```bash
   NEXT_PUBLIC_API_URL=https://your-backend-api.com
   NEXT_PUBLIC_WS_URL=wss://your-backend-api.com
   NEXT_PUBLIC_ENVIRONMENT=production
   NEXT_PUBLIC_APP_NAME=NSAI Orchestrator MCP
   NEXT_PUBLIC_APP_VERSION=1.0.0
   ```

4. **Deploy**
   - Click "Deploy"
   - Vercel will automatically build and deploy your frontend

### Method 2: Deploy via Vercel CLI

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy from Repository Root**
   ```bash
   vercel --prod
   ```

4. **Configure Project Settings**
   - Follow the prompts to configure your project
   - Set the same environment variables as Method 1

### Method 3: Automatic Deployment via GitHub Actions

The repository includes GitHub Actions that automatically deploy to Vercel on every push to `main`:

1. **Set GitHub Secrets**
   Go to your GitHub repository settings → Secrets → Actions, and add:
   ```
   VERCEL_TOKEN=your_vercel_token
   VERCEL_ORG_ID=your_org_id
   VERCEL_PROJECT_ID=your_project_id
   ```

2. **Get Vercel Credentials**
   ```bash
   # Get your Vercel token
   vercel login
   vercel whoami
   
   # Get project IDs
   cd frontend
   vercel link
   ```

3. **Push to Main Branch**
   ```bash
   git push origin main
   ```
   The GitHub Action will automatically deploy to Vercel.

## 🖥 Backend Deployment Options

The frontend requires a backend API. Choose one of these deployment options:

### Option 1: Railway (Recommended)

Railway provides excellent Docker support and is perfect for full-stack applications.

1. **Sign up**: [railway.app](https://railway.app)
2. **Connect GitHub**: Link your repository
3. **Deploy**: 
   ```bash
   # Deploy with Railway CLI
   npm install -g @railway/cli
   railway login
   railway deploy
   ```

### Option 2: Render

Great for Docker deployments with built-in database options.

1. **Sign up**: [render.com](https://render.com)
2. **Create Web Service**: Connect your GitHub repository
3. **Configure**:
   - **Runtime**: Docker
   - **Dockerfile**: Use the production Dockerfile
   - **Environment Variables**: Set all required variables

### Option 3: DigitalOcean App Platform

Excellent for scalable applications with database integration.

1. **Sign up**: [digitalocean.com](https://digitalocean.com)
2. **Create App**: From GitHub repository
3. **Configure Services**:
   - **Web Service**: Your main application
   - **Database**: Redis and PostgreSQL (if not using Neo4j)

### Option 4: AWS/GCP/Azure

For enterprise deployments, use container services:

- **AWS**: ECS, EKS, or App Runner
- **GCP**: Cloud Run, GKE, or App Engine
- **Azure**: Container Instances, AKS, or App Service

## 🔗 Full Stack Deployment

For a complete deployment including databases:

### Docker Compose Deployment

1. **Prepare Production Environment**
   ```bash
   # Clone repository
   git clone https://github.com/ehudso7/nsai-orchestrator-mcp.git
   cd nsai-orchestrator-mcp
   
   # Set up environment
   cp .env.example .env
   # Edit .env with production values
   ```

2. **Deploy with Docker Compose**
   ```bash
   # Production deployment
   docker-compose -f docker-compose.production.yml up -d
   
   # Scale services
   docker-compose -f docker-compose.production.yml up -d --scale orchestrator=3
   ```

3. **Set Up SSL/HTTPS**
   - Configure Nginx with SSL certificates
   - Use Let's Encrypt for free SSL certificates

### Kubernetes Deployment

1. **Prepare Kubernetes Manifests**
   ```bash
   # Apply namespace and configurations
   kubectl apply -f deploy/kubernetes/namespace.yaml
   kubectl apply -f deploy/kubernetes/configmap.yaml
   kubectl apply -f deploy/kubernetes/secrets.yaml
   ```

2. **Deploy Applications**
   ```bash
   # Apply all Kubernetes manifests
   kubectl apply -f deploy/kubernetes/
   ```

3. **Configure Ingress**
   ```yaml
   # ingress.yaml
   apiVersion: networking.k8s.io/v1
   kind: Ingress
   metadata:
     name: nsai-orchestrator-ingress
   spec:
     rules:
     - host: api.your-domain.com
       http:
         paths:
         - path: /
           pathType: Prefix
           backend:
             service:
               name: orchestrator-service
               port:
                 number: 8000
   ```

## 🔧 Environment Variables

### Frontend Variables (Vercel)

Required environment variables for the frontend:

```bash
# API Configuration
NEXT_PUBLIC_API_URL=https://your-backend-api.com
NEXT_PUBLIC_WS_URL=wss://your-backend-api.com

# Application Settings
NEXT_PUBLIC_APP_NAME=NSAI Orchestrator MCP
NEXT_PUBLIC_APP_VERSION=1.0.0
NEXT_PUBLIC_ENVIRONMENT=production

# Feature Flags
NEXT_PUBLIC_ENABLE_ANALYTICS=true
NEXT_PUBLIC_ENABLE_ERROR_REPORTING=true
NEXT_PUBLIC_ENABLE_WEBSOCKETS=true

# Optional: Analytics & Error Reporting
NEXT_PUBLIC_GOOGLE_ANALYTICS_ID=GA_MEASUREMENT_ID
NEXT_PUBLIC_SENTRY_DSN=your_sentry_dsn
```

### Backend Variables

Required environment variables for the backend:

```bash
# Core Settings
APP_NAME=NSAI Orchestrator MCP
APP_VERSION=1.0.0
DEBUG_MODE=false
LOG_LEVEL=INFO

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_SECRET=your-jwt-secret-key-change-this-in-production

# API Keys
ANTHROPIC_API_KEY=your_anthropic_api_key
OPENAI_API_KEY=your_openai_api_key

# Database Configuration
REDIS_URL=redis://redis:6379
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password

# Rate Limiting
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_WINDOW=3600

# Monitoring
PROMETHEUS_ENABLED=true
METRICS_PORT=8001
```

## ✅ Post-Deployment Setup

### 1. Verify Frontend Deployment

1. **Check Vercel Deployment**
   - Visit your Vercel dashboard
   - Confirm deployment status is "Ready"
   - Test the frontend URL

2. **Test API Connection**
   ```bash
   # Test API connectivity from frontend
   curl https://your-frontend.vercel.app/api/health
   ```

### 2. Verify Backend Deployment

1. **Health Checks**
   ```bash
   # Backend health check
   curl https://your-backend-api.com/health
   
   # Database connectivity
   curl https://your-backend-api.com/api/system/status
   ```

2. **Test WebSocket Connection**
   ```javascript
   // Test WebSocket in browser console
   const ws = new WebSocket('wss://your-backend-api.com/ws');
   ws.onopen = () => console.log('WebSocket connected');
   ws.onerror = (error) => console.error('WebSocket error:', error);
   ```

### 3. Configure Monitoring

1. **Set Up Alerts**
   - Configure uptime monitoring (UptimeRobot, Pingdom)
   - Set up error tracking (Sentry)
   - Configure log aggregation

2. **Performance Monitoring**
   - Enable Vercel Analytics
   - Set up backend monitoring (New Relic, DataDog)

## 🐛 Troubleshooting

### Common Issues

#### Frontend Deployment Issues

**Build Failures**
```bash
# Check build logs in Vercel dashboard
# Common fixes:
npm install --legacy-peer-deps
npm run build
```

**Environment Variable Issues**
```bash
# Verify environment variables in Vercel dashboard
# Ensure NEXT_PUBLIC_ prefix for client-side variables
```

**API Connection Issues**
```bash
# Check CORS configuration on backend
# Verify API_URL is correct and accessible
# Test API endpoint directly
curl https://your-backend-api.com/api/health
```

#### Backend Deployment Issues

**Database Connection**
```bash
# Check database URLs and credentials
# Verify network connectivity
# Check firewall settings
```

**Memory Issues**
```bash
# Monitor memory usage
docker stats
# Scale up resources if needed
```

**SSL/HTTPS Issues**
```bash
# Verify SSL certificates
openssl s_client -connect your-domain.com:443
# Check certificate expiration
```

### Getting Help

1. **Check Logs**
   - Vercel: Function logs in dashboard
   - Backend: Application logs and container logs

2. **Monitor Metrics**
   - Response times and error rates
   - Database performance
   - Memory and CPU usage

3. **Community Support**
   - GitHub Issues: Report bugs
   - GitHub Discussions: Ask questions
   - Email: team@nsai.dev

## 🎉 Success!

Once deployed, you'll have:

- ✅ **Frontend**: Deployed on Vercel with global CDN
- ✅ **Backend**: Running on your chosen platform
- ✅ **Databases**: Redis and Neo4j for optimal performance
- ✅ **Monitoring**: Full observability stack
- ✅ **Security**: Production-grade security measures
- ✅ **CI/CD**: Automated deployments on every push

Your NSAI Orchestrator MCP is now ready for production use! 🚀

---

**Need help?** Check our [troubleshooting guide](#troubleshooting) or [contact support](mailto:team@nsai.dev).