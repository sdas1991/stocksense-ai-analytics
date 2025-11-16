# StockSense AI - Deployment Guide

Complete guide for deploying StockSense AI in development and production environments.

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Development Mode](#development-mode)
3. [Production Mode](#production-mode)
4. [Environment Variables](#environment-variables)
5. [Docker Compose Profiles](#docker-compose-profiles)
6. [Monitoring & Logs](#monitoring--logs)
7. [Backup & Recovery](#backup--recovery)
8. [Scaling](#scaling)
9. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### Development Mode (Recommended for Local)

```bash
# Clone the repository
git clone <repository-url>
cd stocksense-ai-analytics

# Run development mode
./run-dev.sh

# Or manually:
docker-compose -f docker-compose.dev.yml up --build
```

**Access**:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8080
- API Docs: http://localhost:8080/docs
- PostgreSQL: localhost:5432
- Redis: localhost:6379

### Production Mode

```bash
# Create production environment file
cp .env.prod.example .env.prod

# Edit with your production values
nano .env.prod

# Run production mode
./run-prod.sh

# Or manually:
docker-compose -f docker-compose.prod.yml up -d
```

**Access**:
- Application: http://localhost (via Nginx)
- API: http://localhost/api
- API Docs: http://localhost/docs

---

## 🔧 Development Mode

### Features

- **Hot Reload**: Code changes automatically reload
- **Debug Logging**: Detailed logs for debugging
- **Volume Mounting**: Live code editing
- **No Authentication**: Easier testing
- **Local Ports**: Direct access to all services

### Starting Development Environment

```bash
# Method 1: Using helper script
./run-dev.sh

# Method 2: Using docker-compose
docker-compose -f docker-compose.dev.yml up

# Method 3: Build and run in background
docker-compose -f docker-compose.dev.yml up -d

# Method 4: Rebuild from scratch
docker-compose -f docker-compose.dev.yml up --build --force-recreate
```

### Development Services

| Service | Container Name | Port | Access |
|---------|---------------|------|--------|
| Frontend | stocksense-frontend-dev | 3000 | http://localhost:3000 |
| Backend | stocksense-backend-dev | 8080 | http://localhost:8080 |
| PostgreSQL | stocksense-db-dev | 5432 | localhost:5432 |
| Redis | stocksense-redis-dev | 6379 | localhost:6379 |

### Development Workflow

1. **Make Code Changes**: Edit files in `backend/` or `frontend/`
2. **Auto Reload**: Changes automatically reload (no restart needed)
3. **Check Logs**: `docker-compose -f docker-compose.dev.yml logs -f backend`
4. **Test API**: Visit http://localhost:8080/docs
5. **Database Access**: `docker exec -it stocksense-db-dev psql -U postgres -d stocksense_dev`

### Useful Dev Commands

```bash
# View logs
docker-compose -f docker-compose.dev.yml logs -f

# View specific service logs
docker-compose -f docker-compose.dev.yml logs -f backend

# Restart a service
docker-compose -f docker-compose.dev.yml restart backend

# Stop all services
docker-compose -f docker-compose.dev.yml down

# Stop and remove volumes (CAUTION: Deletes data)
docker-compose -f docker-compose.dev.yml down -v

# Run database migrations
docker exec -it stocksense-backend-dev alembic upgrade head

# Access backend shell
docker exec -it stocksense-backend-dev python

# Access PostgreSQL
docker exec -it stocksense-db-dev psql -U postgres -d stocksense_dev

# Access Redis CLI
docker exec -it stocksense-redis-dev redis-cli

# Run tests
docker exec -it stocksense-backend-dev pytest
```

---

## 🏭 Production Mode

### Features

- **Nginx Reverse Proxy**: Load balancing and SSL termination
- **Optimized Builds**: Minified and production-ready code
- **Security Hardening**: Authentication, rate limiting, CORS
- **Resource Limits**: CPU and memory constraints
- **Health Checks**: Auto-restart on failures
- **Persistent Data**: Volumes for database and cache

### Prerequisites

1. **Server Requirements**:
   - Linux server (Ubuntu 20.04+ recommended)
   - Docker 20.10+
   - Docker Compose 2.0+
   - 2GB+ RAM
   - 20GB+ disk space

2. **Domain & SSL** (Optional but recommended):
   - Domain name pointing to your server
   - SSL certificate (Let's Encrypt recommended)

### Production Setup

#### Step 1: Configure Environment

```bash
# Create production env file
cp .env.prod.example .env.prod

# Generate strong passwords
openssl rand -base64 32  # For POSTGRES_PASSWORD
openssl rand -base64 32  # For REDIS_PASSWORD
openssl rand -hex 32     # For SECRET_KEY

# Edit configuration
nano .env.prod
```

**Required Variables**:
```bash
POSTGRES_PASSWORD=your_strong_postgres_password
REDIS_PASSWORD=your_strong_redis_password
SECRET_KEY=your_secret_key_for_jwt
AWS_ACCESS_KEY_ID=your_aws_key  # If using Bedrock
AWS_SECRET_ACCESS_KEY=your_aws_secret  # If using Bedrock
```

#### Step 2: Configure Domain (Optional)

Edit `nginx/conf.d/stocksense.conf`:
```nginx
server_name yourdomain.com www.yourdomain.com;
```

#### Step 3: Setup SSL (Recommended)

```bash
# Using Let's Encrypt with Certbot
sudo apt-get install certbot

# Generate certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Copy certificates
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/key.pem

# Update nginx config to enable SSL
nano nginx/conf.d/stocksense.conf
# Uncomment SSL lines
```

#### Step 4: Deploy

```bash
# Run production deployment
./run-prod.sh

# Or manually
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Production Services

| Service | Container Name | Internal Port | External Access |
|---------|---------------|---------------|-----------------|
| Nginx | stocksense-nginx-prod | 80, 443 | http://yourdomain.com |
| Backend | stocksense-backend-prod | 8080 | /api (via Nginx) |
| Frontend | stocksense-frontend-prod | 80 | / (via Nginx) |
| PostgreSQL | stocksense-db-prod | 5432 | localhost:5433 |
| Redis | stocksense-redis-prod | 6379 | localhost:6380 |

### Production Monitoring

```bash
# Check service health
docker-compose -f docker-compose.prod.yml ps

# View resource usage
docker stats

# Check logs
docker-compose -f docker-compose.prod.yml logs -f

# Check backend health
curl http://localhost/api/health

# Check Redis stats
docker exec -it stocksense-redis-prod redis-cli -a $REDIS_PASSWORD info
```

---

## 🔐 Environment Variables

### Development (.env)

```bash
# Minimal configuration for dev
DEBUG=True
ENV=development
DATABASE_URL=postgresql://postgres:devpassword123@postgres-db:5432/stocksense_dev
REDIS_URL=redis://redis-cache:6379/0
```

### Production (.env.prod)

```bash
# Required
POSTGRES_USER=stocksense_user
POSTGRES_PASSWORD=<strong-password>
POSTGRES_DB=stocksense_prod
REDIS_PASSWORD=<strong-password>
SECRET_KEY=<random-secret-key>

# Optional but recommended
AWS_ACCESS_KEY_ID=<your-key>
AWS_SECRET_ACCESS_KEY=<your-secret>
AWS_REGION=us-east-1

# Email (for alerts)
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# API Keys
NEWS_API_KEY=<your-key>
ALPHA_VANTAGE_API_KEY=<your-key>
```

---

## 📊 Monitoring & Logs

### Log Locations

**Development**:
```bash
# Real-time logs
docker-compose -f docker-compose.dev.yml logs -f

# Service-specific
docker logs stocksense-backend-dev -f
docker logs stocksense-frontend-dev -f
```

**Production**:
```bash
# Nginx logs
tail -f nginx/logs/access.log
tail -f nginx/logs/error.log

# Application logs
docker-compose -f docker-compose.prod.yml logs -f backend

# Database logs
docker logs stocksense-db-prod
```

### Health Checks

```bash
# Backend health
curl http://localhost:8080/api/health  # Dev
curl http://localhost/api/health       # Prod

# Database connectivity
docker exec -it stocksense-db-prod pg_isready -U stocksense_user

# Redis connectivity
docker exec -it stocksense-redis-prod redis-cli ping
```

### Metrics

**Backend metrics available at** `/api/health`:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00",
  "services": {
    "database": "connected",
    "redis": "connected",
    "bedrock": "available"
  }
}
```

---

## 💾 Backup & Recovery

### Database Backup

```bash
# Create backup
docker exec stocksense-db-prod pg_dump -U stocksense_user stocksense_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# Automated daily backup
crontab -e
# Add: 0 2 * * * /path/to/backup-script.sh
```

**backup-script.sh**:
```bash
#!/bin/bash
BACKUP_DIR="/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
docker exec stocksense-db-prod pg_dump -U stocksense_user stocksense_prod > $BACKUP_DIR/backup_$DATE.sql
# Keep only last 7 days
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete
```

### Database Restore

```bash
# Restore from backup
docker exec -i stocksense-db-prod psql -U stocksense_user stocksense_prod < backup.sql
```

### Redis Backup

Redis persistence is enabled with AOF (Append Only File):
```bash
# Backup Redis data
docker exec stocksense-redis-prod redis-cli -a $REDIS_PASSWORD BGSAVE

# Copy backup
docker cp stocksense-redis-prod:/data/dump.rdb ./redis-backup.rdb
```

---

## 📈 Scaling

### Horizontal Scaling

**Scale backend instances**:
```yaml
# In docker-compose.prod.yml
backend:
  deploy:
    replicas: 4  # Increase replicas
```

### Vertical Scaling

**Increase resources**:
```yaml
backend:
  deploy:
    resources:
      limits:
        cpus: '2'
        memory: 2G
```

### Database Scaling

**Enable read replicas** (advanced):
1. Setup PostgreSQL streaming replication
2. Configure connection pooling (PgBouncer)
3. Route read queries to replicas

---

## 🔍 Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Find process using port
sudo lsof -i :3000
sudo lsof -i :8080

# Kill process or change port in docker-compose
```

#### Database Connection Failed
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Check logs
docker logs stocksense-db-prod

# Verify credentials in .env.prod
```

#### Redis Connection Failed
```bash
# Check Redis status
docker exec stocksense-redis-prod redis-cli ping

# Check password
docker exec stocksense-redis-prod redis-cli -a $REDIS_PASSWORD ping
```

#### Nginx 502 Bad Gateway
```bash
# Check backend is running
curl http://localhost:8080/api/health

# Check nginx logs
tail -f nginx/logs/error.log

# Restart services
docker-compose -f docker-compose.prod.yml restart
```

#### Out of Memory
```bash
# Check memory usage
docker stats

# Reduce replicas or increase server RAM
# Or add resource limits
```

### Debug Mode

**Enable debug logging**:
```bash
# In .env or docker-compose
LOG_LEVEL=DEBUG
DEBUG=True

# Restart service
docker-compose restart backend
```

---

## 📚 Additional Resources

- **API Documentation**: http://localhost:8080/docs (dev) or http://yourdomain.com/docs (prod)
- **Docker Docs**: https://docs.docker.com
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Vue.js Docs**: https://vuejs.org
- **PostgreSQL Docs**: https://www.postgresql.org/docs
- **Redis Docs**: https://redis.io/docs

---

## 🎯 Best Practices

1. **Never commit** `.env` or `.env.prod` files
2. **Use strong passwords** for production
3. **Enable SSL** in production
4. **Regular backups** of database
5. **Monitor logs** regularly
6. **Update dependencies** periodically
7. **Use secrets management** (Vault, AWS Secrets Manager)
8. **Implement rate limiting** on public APIs
9. **Setup monitoring** (Prometheus, Grafana)
10. **Regular security audits**

---

## ✅ Deployment Checklist

### Development

- [ ] Docker and Docker Compose installed
- [ ] Ports 3000, 8080, 5432, 6379 available
- [ ] Run `./run-dev.sh`
- [ ] Access http://localhost:3000
- [ ] Test stock analysis

### Production

- [ ] Server with 2GB+ RAM
- [ ] Domain configured (optional)
- [ ] SSL certificates obtained (recommended)
- [ ] `.env.prod` configured with strong passwords
- [ ] Nginx configuration updated with domain
- [ ] Firewall rules configured (80, 443)
- [ ] Backups scheduled
- [ ] Monitoring setup
- [ ] Run `./run-prod.sh`
- [ ] Test all endpoints
- [ ] Setup auto-start on boot

---

## 🆘 Support

For issues or questions:
- Check logs: `docker-compose logs -f`
- Review this guide
- Check GitHub issues
- Review API documentation at `/docs`

---

**Happy Deploying! 🚀**
