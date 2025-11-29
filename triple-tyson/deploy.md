# 🚀 Deployment Guide

## Crisis Response Coordinator Agent - Production Deployment

This guide covers deploying the Crisis Response Coordinator to Google Cloud Run.

---

## Prerequisites

1. **Google Cloud Account** with billing enabled
2. **gcloud CLI** installed ([Install guide](https://cloud.google.com/sdk/docs/install))
3. **Docker** installed locally (for testing)

---

## Quick Deploy to Google Cloud Run

### 1. Set up Google Cloud Project

```bash
# Login to Google Cloud
gcloud auth login

# Set your project ID
export PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### 2. Build and Deploy

```bash
# Set environment variables
export REGION="us-central1"
export SERVICE_NAME="crisis-response-agent"

# Build and deploy in one command
gcloud run deploy $SERVICE_NAME \
  --source . \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY="your-gemini-api-key" \
  --memory 512Mi \
  --cpu 1 \
  --timeout 60s \
  --max-instances 10

# Get the service URL
gcloud run services describe $SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --format 'value(status.url)'
```

### 3. Test Deployment

```bash
# Get your service URL
export SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --format 'value(status.url)')

# Test health endpoint
curl $SERVICE_URL/health

# Test crisis detection
curl -X POST $SERVICE_URL/detect \
  -H "Content-Type: application/json" \
  -d '{
    "crisis_description": "My friend is having chest pain",
    "country": "USA"
  }'
```

---

## Alternative: Docker Local Deployment

### Build Docker Image

```bash
# Build the image
docker build -t crisis-response-agent .

# Run locally
docker run -p 8080:8080 \
  -e GOOGLE_API_KEY="your-api-key" \
  crisis-response-agent

# Test
curl http://localhost:8080/health
```

### Push to Google Container Registry

```bash
# Tag image
docker tag crisis-response-agent gcr.io/$PROJECT_ID/crisis-response-agent

# Configure Docker for GCR
gcloud auth configure-docker

# Push image
docker push gcr.io/$PROJECT_ID/crisis-response-agent

# Deploy from GCR
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/crisis-response-agent \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated
```

---

## Environment Variables

Set these in Cloud Run:

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_API_KEY` | Gemini API key | Yes |
| `DEFAULT_COUNTRY` | Default country code | No (default: USA) |
| `PORT` | Server port | No (default: 8080) |

```bash
# Update environment variables
gcloud run services update $SERVICE_NAME \
  --set-env-vars GOOGLE_API_KEY="new-key",DEFAULT_COUNTRY="India" \
  --region $REGION
```

---

## API Endpoints

Once deployed, your service exposes:

### `GET /`
Health check and API documentation

### `POST /detect`
Main crisis detection endpoint

**Request:**
```json
{
  "crisis_description": "I'm having a panic attack",
  "country": "USA"
}
```

**Response:**
```json
{
  "success": true,
  "case_id": "CASE-00001",
  "classification": {
    "category": "mental_health_crisis",
    "severity": "medium"
  },
  "response": "formatted crisis response...",
  "timestamp": "2025-11-29T12:00:00"
}
```

### `GET /cases`
List all active cases

### `GET /case/<case_id>`
Get specific case details

### `GET /health`
Detailed health check with metrics

---

## Monitoring & Logs

### View Logs

```bash
# Stream logs
gcloud run services logs tail $SERVICE_NAME \
  --region $REGION

# View in Cloud Console
gcloud run services describe $SERVICE_NAME \
  --region $REGION \
  --format 'value(status.url)' | \
  sed 's|https://||' | \
  xargs -I {} echo "https://console.cloud.google.com/run/detail/$REGION/$SERVICE_NAME/logs"
```

### Metrics

Cloud Run automatically provides:
- Request count
- Request latency
- Error rate
- Container CPU/memory usage

Access at: [Cloud Run Console](https://console.cloud.google.com/run)

---

## Scaling Configuration

### Auto-scaling

```bash
# Set min/max instances
gcloud run services update $SERVICE_NAME \
  --min-instances 0 \
  --max-instances 10 \
  --region $REGION

# Set concurrency
gcloud run services update $SERVICE_NAME \
  --concurrency 80 \
  --region $REGION
```

### Resource Limits

```bash
# Increase memory and CPU
gcloud run services update $SERVICE_NAME \
  --memory 1Gi \
  --cpu 2 \
  --region $REGION
```

---

## Security Best Practices

### 1. Use Secret Manager for API Keys

```bash
# Create secret
echo -n "your-api-key" | gcloud secrets create gemini-api-key --data-file=-

# Grant access to Cloud Run service account
gcloud secrets add-iam-policy-binding gemini-api-key \
  --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Deploy with secret
gcloud run deploy $SERVICE_NAME \
  --set-secrets GOOGLE_API_KEY=gemini-api-key:latest \
  --region $REGION
```

### 2. Enable Authentication (Optional)

```bash
# Require authentication
gcloud run services update $SERVICE_NAME \
  --no-allow-unauthenticated \
  --region $REGION

# Test with auth
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  $SERVICE_URL/health
```

### 3. Set up VPC Connector (for private resources)

```bash
# Create VPC connector
gcloud compute networks vpc-access connectors create crisis-connector \
  --network default \
  --region $REGION \
  --range 10.8.0.0/28

# Deploy with VPC
gcloud run deploy $SERVICE_NAME \
  --vpc-connector crisis-connector \
  --region $REGION
```

---

## Cost Optimization

### Pricing Estimate

Cloud Run pricing (as of 2025):
- **CPU**: $0.00002400 per vCPU-second
- **Memory**: $0.00000250 per GiB-second
- **Requests**: $0.40 per million requests

**Example**: 10,000 requests/month, 500ms avg duration, 512MB memory
- Cost: ~$0.50/month (within free tier!)

### Free Tier

Cloud Run includes:
- 2 million requests/month
- 360,000 GiB-seconds memory
- 180,000 vCPU-seconds

### Optimization Tips

1. **Use min-instances=0** for low traffic
2. **Optimize cold starts** with smaller images
3. **Cache protocols** in memory (already implemented)
4. **Set appropriate timeouts** (60s default)

---

## Troubleshooting

### Common Issues

**1. Deployment fails**
```bash
# Check logs
gcloud run services logs read $SERVICE_NAME --region $REGION

# Verify Dockerfile builds locally
docker build -t test .
```

**2. API key not working**
```bash
# Verify secret
gcloud secrets versions access latest --secret gemini-api-key

# Check environment variables
gcloud run services describe $SERVICE_NAME \
  --region $REGION \
  --format 'value(spec.template.spec.containers[0].env)'
```

**3. Timeout errors**
```bash
# Increase timeout
gcloud run services update $SERVICE_NAME \
  --timeout 300s \
  --region $REGION
```

---

## CI/CD Integration

### GitHub Actions Example

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Cloud Run

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - uses: google-github-actions/setup-gcloud@v0
        with:
          service_account_key: ${{ secrets.GCP_SA_KEY }}
          project_id: ${{ secrets.GCP_PROJECT_ID }}
      
      - name: Deploy
        run: |
          gcloud run deploy crisis-response-agent \
            --source . \
            --region us-central1 \
            --allow-unauthenticated
```

---

## Production Checklist

Before going live:

- [ ] API key stored in Secret Manager
- [ ] Monitoring and alerting configured
- [ ] Error tracking set up (e.g., Sentry)
- [ ] Rate limiting implemented
- [ ] HTTPS enforced (automatic with Cloud Run)
- [ ] CORS configured for your domain
- [ ] Backup strategy for cases.json
- [ ] Load testing completed
- [ ] Documentation updated with live URL

---

## Support & Resources

- **Cloud Run Docs**: https://cloud.google.com/run/docs
- **Pricing Calculator**: https://cloud.google.com/products/calculator
- **Support**: https://cloud.google.com/support

---

## Quick Reference

```bash
# Deploy
gcloud run deploy crisis-response-agent --source . --region us-central1

# Update
gcloud run services update crisis-response-agent --set-env-vars KEY=value

# Delete
gcloud run services delete crisis-response-agent --region us-central1

# Logs
gcloud run services logs tail crisis-response-agent

# URL
gcloud run services describe crisis-response-agent --format 'value(status.url)'
```

---

**Deployed URL**: Add your Cloud Run URL here after deployment

**Status**: ✅ Production Ready

**Last Updated**: November 29, 2025
