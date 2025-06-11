# 🚀 Vercel Deployment Guide

## Quick Deploy

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fehudso7%2Fnsai-orchestrator-mcp&project-name=nsai-orchestrator&root-directory=frontend&env=NEXT_PUBLIC_API_URL&envDescription=API%20endpoint%20URL)

## Manual Deployment Steps

### 1. Connect GitHub Repository

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "Add New Project"
3. Import from GitHub: `ehudso7/nsai-orchestrator-mcp`
4. Select the repository

### 2. Configure Project

**Root Directory**: `frontend`

**Framework Preset**: Next.js

**Build Settings**:
- Build Command: `npm run build`
- Output Directory: `.next`
- Install Command: `npm install`

### 3. Environment Variables

Add the following environment variable:

```
NEXT_PUBLIC_API_URL=https://your-api-endpoint.com
```

For local development/testing, use:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 4. Deploy

Click "Deploy" and wait for the build to complete.

## Post-Deployment

### Custom Domain

1. Go to Project Settings > Domains
2. Add your custom domain
3. Configure DNS as instructed

### Environment Variables for Production

```
NEXT_PUBLIC_API_URL=https://api.your-domain.com
NEXT_PUBLIC_WS_URL=wss://ws.your-domain.com
```

### Performance Monitoring

Vercel automatically provides:
- Web Vitals monitoring
- Real User Monitoring (RUM)
- Build & Function logs

## Deployment Status

Your deployment will be available at:
- Production: `https://nsai-orchestrator.vercel.app`
- Preview: `https://nsai-orchestrator-git-[branch]-[username].vercel.app`

## Troubleshooting

### Build Failures

1. Check build logs in Vercel dashboard
2. Ensure all dependencies are in `package.json`
3. Verify environment variables are set

### API Connection Issues

1. Ensure CORS is configured on your API
2. Use HTTPS for production API endpoints
3. Check browser console for errors

## Success Metrics

After deployment, you should see:
- ✅ Lighthouse score: 95+
- ✅ First Contentful Paint: <1s
- ✅ Time to Interactive: <2s
- ✅ No console errors
- ✅ All API endpoints connected

## Support

For issues, check:
1. [Vercel Documentation](https://vercel.com/docs)
2. [Next.js Documentation](https://nextjs.org/docs)
3. Project issues: https://github.com/ehudso7/nsai-orchestrator-mcp/issues