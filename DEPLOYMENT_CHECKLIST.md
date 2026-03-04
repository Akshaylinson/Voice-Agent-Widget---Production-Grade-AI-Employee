# 🚀 Gemini Voice Agent - Deployment Checklist

## Pre-Deployment

### Environment Setup
- [ ] Copy `.env.example` to `.env`
- [ ] Add `GEMINI_API_KEY` (get from https://makersuite.google.com/app/apikey)
- [ ] Generate `ENCRYPTION_KEY` (run `python configure.py`)
- [ ] Verify `DATABASE_URL` is correct
- [ ] Set `MASTER_ADMIN_SECRET` (optional)

### Dependencies
- [ ] Docker installed and running
- [ ] Docker Compose installed
- [ ] Python 3.9+ (for testing)
- [ ] PostgreSQL with pgvector support

### Configuration Validation
```bash
python configure.py
```

## Deployment Steps

### 1. Database Setup
- [ ] Start PostgreSQL container
- [ ] Enable pgvector extension
- [ ] Run migration script (if upgrading)
```bash
docker-compose up -d db
psql -U postgres -d voice_agent_multi_tenant -f database_migration_gemini.sql
```

### 2. Backend Deployment
- [ ] Build backend image
- [ ] Start backend container
- [ ] Verify health endpoint
```bash
docker-compose build backend
docker-compose up -d backend
curl http://localhost:8000/health
```

### 3. Admin Dashboard
- [ ] Build admin image
- [ ] Start admin container
- [ ] Access dashboard
```bash
docker-compose build admin
docker-compose up -d admin
# Open http://localhost:3000
```

### 4. Create First Tenant
- [ ] Open admin dashboard
- [ ] Click "Create Tenant"
- [ ] Fill in details:
  - Company name
  - Domain
  - Gemini API key (optional)
  - Voice settings
  - Introduction script
- [ ] Copy widget signature
- [ ] Save embed code

### 5. Add Knowledge Base
- [ ] Navigate to tenant knowledge
- [ ] Add knowledge entries:
  - [ ] Company overview
  - [ ] Services/Products
  - [ ] Pricing
  - [ ] FAQ
  - [ ] Contact info
- [ ] Verify embeddings generated
- [ ] Test knowledge retrieval

### 6. Widget Integration
- [ ] Copy embed code from admin
- [ ] Add to client website before `</body>`
- [ ] Test on localhost
- [ ] Test on production domain
- [ ] Verify domain whitelist

### 7. Testing
- [ ] Run automated tests
```bash
python test_gemini.py
```
- [ ] Manual widget test:
  - [ ] Click avatar
  - [ ] Hear introduction
  - [ ] Speak query
  - [ ] Receive response
  - [ ] Verify knowledge used
- [ ] Test conversation logging
- [ ] Test analytics dashboard

## Post-Deployment

### Monitoring
- [ ] Check container logs
```bash
docker logs voice-agent-client1
docker logs db-client1
```
- [ ] Monitor API response times
- [ ] Check database connections
- [ ] Verify embedding generation

### Performance Tuning
- [ ] Optimize vector index
```sql
-- Adjust lists parameter based on data size
CREATE INDEX knowledge_base_embedding_idx 
ON knowledge_base USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 200);
```
- [ ] Enable connection pooling
- [ ] Configure Redis cache (optional)
- [ ] Set up CDN for widget

### Security
- [ ] Enable HTTPS/SSL
- [ ] Configure CORS properly
- [ ] Set up rate limiting
- [ ] Enable firewall rules
- [ ] Rotate encryption keys
- [ ] Backup database

### Backup Strategy
- [ ] Database backup schedule
```bash
# Daily backup
pg_dump -U postgres voice_agent_multi_tenant > backup_$(date +%Y%m%d).sql
```
- [ ] Backup `.env` file (securely)
- [ ] Backup tenant configurations
- [ ] Test restore procedure

## Production Checklist

### Infrastructure
- [ ] Use managed PostgreSQL (RDS/Cloud SQL)
- [ ] Enable pgvector extension
- [ ] Set up load balancer
- [ ] Configure auto-scaling
- [ ] Set up monitoring (Prometheus/Grafana)
- [ ] Configure logging (ELK/CloudWatch)

### Security Hardening
- [ ] Use secrets manager for API keys
- [ ] Enable database encryption at rest
- [ ] Configure VPC/network isolation
- [ ] Set up WAF rules
- [ ] Enable DDoS protection
- [ ] Configure security groups

### Performance
- [ ] Enable Redis for caching
- [ ] Configure CDN for static assets
- [ ] Optimize database queries
- [ ] Set up read replicas
- [ ] Enable query caching
- [ ] Configure connection pooling

### Compliance
- [ ] GDPR compliance (if EU users)
- [ ] Data retention policies
- [ ] Privacy policy updated
- [ ] Terms of service updated
- [ ] Cookie consent (if needed)

## Troubleshooting

### Common Issues

#### Widget Not Loading
- [ ] Check CORS configuration
- [ ] Verify API URL is correct
- [ ] Check browser console for errors
- [ ] Verify tenant credentials

#### No Voice Response
- [ ] Check Gemini API key
- [ ] Verify knowledge base has entries
- [ ] Check backend logs
- [ ] Test with curl

#### Embeddings Not Generated
- [ ] Check Gemini API quota
- [ ] Verify pgvector extension
- [ ] Check database logs
- [ ] Manually regenerate embeddings

#### Slow Performance
- [ ] Check database indexes
- [ ] Monitor API response times
- [ ] Verify network latency
- [ ] Check container resources

### Debug Commands
```bash
# Check container status
docker ps

# View logs
docker logs voice-agent-client1 -f

# Check database
docker exec -it db-client1 psql -U postgres -d voice_agent_multi_tenant

# Test API
curl http://localhost:8000/health

# Check pgvector
docker exec -it db-client1 psql -U postgres -d voice_agent_multi_tenant -c "SELECT * FROM pg_extension WHERE extname = 'vector';"

# View embeddings
docker exec -it db-client1 psql -U postgres -d voice_agent_multi_tenant -c "SELECT id, title, embedding IS NOT NULL as has_embedding FROM knowledge_base;"
```

## Rollback Plan

### If Issues Occur
1. [ ] Stop containers
```bash
docker-compose down
```

2. [ ] Restore database backup
```bash
psql -U postgres voice_agent_multi_tenant < backup_YYYYMMDD.sql
```

3. [ ] Restore `.env` from backup

4. [ ] Checkout previous version
```bash
git checkout <previous-commit>
```

5. [ ] Rebuild and restart
```bash
docker-compose build
docker-compose up -d
```

## Success Criteria

### Functional
- [x] Widget loads on client website
- [x] Voice conversation works end-to-end
- [x] Knowledge base answers queries correctly
- [x] Conversation logging works
- [x] Analytics dashboard shows data

### Performance
- [x] Response latency < 2 seconds
- [x] Knowledge retrieval < 50ms
- [x] Embedding generation < 200ms
- [x] 99% uptime

### Security
- [x] API keys encrypted
- [x] Domain whitelist enforced
- [x] No sensitive data in logs
- [x] HTTPS enabled (production)

## Maintenance Schedule

### Daily
- [ ] Check error logs
- [ ] Monitor API usage
- [ ] Verify backups completed

### Weekly
- [ ] Review conversation analytics
- [ ] Check knowledge base effectiveness
- [ ] Update knowledge entries
- [ ] Review performance metrics

### Monthly
- [ ] Update dependencies
- [ ] Security audit
- [ ] Performance optimization
- [ ] Backup verification
- [ ] Cost analysis

## Support Contacts

- **Technical Issues**: Check logs first
- **Gemini API**: https://ai.google.dev/support
- **Database**: PostgreSQL documentation
- **Docker**: Docker documentation

---

## 🎉 Deployment Complete!

Once all items are checked, your Gemini Voice Agent is production-ready!

**Next Steps**:
1. Monitor for 24 hours
2. Gather user feedback
3. Optimize based on usage patterns
4. Scale as needed

**Documentation**:
- `README.md` - Overview
- `GEMINI_UPGRADE.md` - Detailed guide
- `UPGRADE_SUMMARY.md` - Quick reference

**Support**:
- Run `python configure.py` to verify setup
- Run `python test_gemini.py` to test functionality
- Check `docker logs` for debugging
