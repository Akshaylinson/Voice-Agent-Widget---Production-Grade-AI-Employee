# 🌐 Production Deployment Guide

## Overview

This guide covers deploying the Voice Agent Widget to production cloud environments with SSL, domain configuration, and scalability.

## Architecture for Production

```
Internet
    │
    ▼
Load Balancer (SSL/HTTPS)
    │
    ├─► Voice Agent Container (Client 1) ──► PostgreSQL RDS
    ├─► Voice Agent Container (Client 2) ──► PostgreSQL RDS
    └─► Voice Agent Container (Client 3) ──► PostgreSQL RDS
```

## Prerequisites

- Cloud account (AWS/GCP/Azure)
- Domain name with DNS access
- SSL certificate
- Container registry access
- OpenAI API key

## Option 1: AWS Deployment

### 1. Build and Push Docker Image

```bash
# Build image
docker build -t voice-agent:latest ./backend

# Tag for ECR
docker tag voice-agent:latest <account-id>.dkr.ecr.<region>.amazonaws.com/voice-agent:latest

# Login to ECR
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com

# Push
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/voice-agent:latest
```

### 2. Create RDS PostgreSQL Database

```bash
aws rds create-db-instance \
    --db-instance-identifier voice-agent-client1-db \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --master-username postgres \
    --master-user-password <secure-password> \
    --allocated-storage 20
```

### 3. Deploy to ECS

Create task definition (`task-definition.json`):

```json
{
  "family": "voice-agent-client1",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "voice-agent",
      "image": "<account-id>.dkr.ecr.<region>.amazonaws.com/voice-agent:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "CLIENT_ID",
          "value": "client1"
        },
        {
          "name": "DATABASE_URL",
          "value": "postgresql://postgres:<password>@<rds-endpoint>:5432/voice_agent"
        },
        {
          "name": "OPENAI_API_KEY",
          "value": "<your-openai-key>"
        },
        {
          "name": "JWT_SECRET",
          "value": "<your-jwt-secret>"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/voice-agent",
          "awslogs-region": "<region>",
          "awslogs-stream-prefix": "client1"
        }
      }
    }
  ]
}
```

Deploy:
```bash
aws ecs register-task-definition --cli-input-json file://task-definition.json

aws ecs create-service \
    --cluster voice-agent-cluster \
    --service-name voice-agent-client1 \
    --task-definition voice-agent-client1 \
    --desired-count 1 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[<subnet-id>],securityGroups=[<sg-id>],assignPublicIp=ENABLED}"
```

### 4. Configure Application Load Balancer

```bash
# Create target group
aws elbv2 create-target-group \
    --name voice-agent-client1-tg \
    --protocol HTTP \
    --port 8000 \
    --vpc-id <vpc-id> \
    --target-type ip

# Create load balancer
aws elbv2 create-load-balancer \
    --name voice-agent-lb \
    --subnets <subnet-1> <subnet-2> \
    --security-groups <sg-id>

# Add HTTPS listener with SSL certificate
aws elbv2 create-listener \
    --load-balancer-arn <lb-arn> \
    --protocol HTTPS \
    --port 443 \
    --certificates CertificateArn=<cert-arn> \
    --default-actions Type=forward,TargetGroupArn=<tg-arn>
```

### 5. Configure DNS

Point your domain to the load balancer:

```
voice-api.yourdomain.com → CNAME → <lb-dns-name>
```

## Option 2: Google Cloud Platform (GKE)

### 1. Build and Push to GCR

```bash
# Build
docker build -t gcr.io/<project-id>/voice-agent:latest ./backend

# Push
docker push gcr.io/<project-id>/voice-agent:latest
```

### 2. Create Cloud SQL PostgreSQL

```bash
gcloud sql instances create voice-agent-client1-db \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=us-central1
```

### 3. Deploy to GKE

Create deployment (`deployment.yaml`):

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: voice-agent-client1
spec:
  replicas: 2
  selector:
    matchLabels:
      app: voice-agent-client1
  template:
    metadata:
      labels:
        app: voice-agent-client1
    spec:
      containers:
      - name: voice-agent
        image: gcr.io/<project-id>/voice-agent:latest
        ports:
        - containerPort: 8000
        env:
        - name: CLIENT_ID
          value: "client1"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: voice-agent-secrets
              key: database-url
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: voice-agent-secrets
              key: openai-api-key
---
apiVersion: v1
kind: Service
metadata:
  name: voice-agent-client1-service
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8000
  selector:
    app: voice-agent-client1
```

Deploy:
```bash
kubectl apply -f deployment.yaml
```

## Option 3: Azure (AKS)

### 1. Build and Push to ACR

```bash
# Create ACR
az acr create --resource-group voice-agent-rg --name voiceagentacr --sku Basic

# Build and push
az acr build --registry voiceagentacr --image voice-agent:latest ./backend
```

### 2. Create Azure Database for PostgreSQL

```bash
az postgres server create \
    --resource-group voice-agent-rg \
    --name voice-agent-client1-db \
    --location eastus \
    --admin-user postgres \
    --admin-password <secure-password> \
    --sku-name B_Gen5_1
```

### 3. Deploy to AKS

Similar to GKE deployment with Azure-specific configurations.

## Environment Variables for Production

```bash
# Required
OPENAI_API_KEY=sk-prod-key-here
DATABASE_URL=postgresql://user:pass@host:5432/dbname
CLIENT_ID=client1
JWT_SECRET=secure-random-string-here

# Optional
PORT=8000
LOG_LEVEL=info
CORS_ORIGINS=https://yourdomain.com
```

## SSL/HTTPS Configuration

### Using Let's Encrypt with Nginx

```nginx
server {
    listen 443 ssl http2;
    server_name voice-api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location /api/ {
        proxy_pass http://voice-agent:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /voice-agent-widget.js {
        proxy_pass http://voice-agent:8000/voice-agent-widget.js;
        add_header Access-Control-Allow-Origin *;
    }
}
```

## Widget Embed Code for Production

```html
<script>
window.VOICE_AGENT_API_URL = 'https://voice-api.yourdomain.com/api';
</script>
<script src="https://voice-api.yourdomain.com/voice-agent-widget.js"></script>
```

## Scaling Considerations

### Horizontal Scaling
- Run multiple container instances behind load balancer
- Use container orchestration (ECS/GKE/AKS)
- Configure auto-scaling based on CPU/memory

### Database Optimization
- Use connection pooling
- Enable read replicas for analytics queries
- Regular vacuum and analyze operations

### Caching
- Add Redis for session management
- Cache configuration and knowledge base
- Implement CDN for widget delivery

### Monitoring
- CloudWatch/Stackdriver/Azure Monitor for logs
- Set up alerts for errors and latency
- Track conversation metrics

## Security Best Practices

1. **API Keys**: Store in secrets manager (AWS Secrets Manager/GCP Secret Manager)
2. **Database**: Use private subnets, enable SSL connections
3. **Network**: Configure security groups/firewall rules
4. **CORS**: Restrict to specific domains in production
5. **Rate Limiting**: Implement per-client rate limits
6. **Authentication**: Add API key authentication for admin endpoints

## Cost Optimization

### AWS Estimated Monthly Costs (per client)
- ECS Fargate (0.5 vCPU, 1GB): ~$15
- RDS PostgreSQL (db.t3.micro): ~$15
- ALB: ~$20
- Data transfer: ~$10
- **Total: ~$60/month per client**

### Optimization Tips
- Use reserved instances for predictable workloads
- Enable auto-scaling to scale down during low traffic
- Use spot instances for non-critical environments
- Implement request caching to reduce API calls

## Backup and Disaster Recovery

### Database Backups
```bash
# AWS RDS automated backups
aws rds modify-db-instance \
    --db-instance-identifier voice-agent-client1-db \
    --backup-retention-period 7 \
    --preferred-backup-window "03:00-04:00"
```

### Configuration Backups
- Export client configurations regularly
- Store in version control or S3
- Implement restore procedures

## Multi-Region Deployment

For high availability:
1. Deploy containers in multiple regions
2. Use Route53/Cloud DNS for geo-routing
3. Replicate databases across regions
4. Implement failover mechanisms

## Monitoring and Alerts

### Key Metrics to Monitor
- API response time
- Error rate
- Voice processing latency
- Database connection pool
- Container CPU/memory usage
- Conversation success rate

### Sample CloudWatch Alarms
```bash
aws cloudwatch put-metric-alarm \
    --alarm-name voice-agent-high-error-rate \
    --alarm-description "Alert when error rate exceeds 5%" \
    --metric-name ErrorRate \
    --namespace VoiceAgent \
    --statistic Average \
    --period 300 \
    --threshold 5 \
    --comparison-operator GreaterThanThreshold
```

## Deployment Checklist

- [ ] Domain and SSL certificate configured
- [ ] Database created and secured
- [ ] Environment variables set in secrets manager
- [ ] Container image built and pushed
- [ ] Load balancer configured with health checks
- [ ] DNS records updated
- [ ] CORS configured for client domains
- [ ] Monitoring and alerts set up
- [ ] Backup strategy implemented
- [ ] Security groups/firewall rules configured
- [ ] Widget tested on client website
- [ ] Admin dashboard accessible
- [ ] Documentation provided to client

## Support and Maintenance

### Regular Tasks
- Monitor logs for errors
- Review conversation analytics
- Update knowledge base as needed
- Apply security patches
- Scale resources based on usage
- Optimize database queries

### Client Onboarding
1. Deploy isolated container and database
2. Provide admin dashboard access
3. Configure initial knowledge base
4. Customize branding and voice
5. Test widget integration
6. Provide embed code
7. Monitor first week of usage

---

**Production deployment complete! Your voice agent is now live and scalable.**
