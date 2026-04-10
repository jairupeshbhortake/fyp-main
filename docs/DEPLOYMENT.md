# Deployment Guide

## Docker (recommended)

### Prerequisites
- Docker Engine 24+ and Docker Compose v2

### Steps

```bash
git clone https://github.com/youruser/dronevault-analytics
cd dronevault-analytics

# 1. Configure environment
cp .env.example .env
# Edit .env — set a strong SECRET_KEY at minimum

# 2. Start the stack
docker compose -f docker-compose.prod.yml up -d

# 3. Check logs
docker compose logs -f
```

The frontend is served at **port 80** via Nginx, which proxies `/api` to the backend.

### Updating

```bash
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

---

## PostgreSQL (optional)

For production workloads, replace SQLite with PostgreSQL:

1. Uncomment the `db` service in `docker-compose.prod.yml`.
2. Set `DATABASE_URL=postgresql://dronevault:${POSTGRES_PASSWORD}@db:5432/dronevault` in `.env`.
3. Remove the `connect_args` block in `backend/app/database.py` (SQLite-only).

---

## HTTPS / TLS

Place your certificate and key at `./ssl/cert.pem` and `./ssl/key.pem`, then
uncomment the HTTPS server block in `frontend/nginx.conf`.

For Let's Encrypt, use [Certbot](https://certbot.eff.org/) with the Nginx plugin.

---

## Reverse Proxy (existing Nginx/Traefik)

If you are running behind an existing proxy, expose only the frontend container
and ensure the proxy passes the `X-Forwarded-*` headers.

Add `--proxy-headers` to the uvicorn command in `docker-compose.prod.yml` when
behind a reverse proxy.

---

## Backup

The SQLite database and uploaded files live in the `dronevault-data` Docker volume.

```bash
# Backup
docker run --rm -v dronevault-data:/data -v $(pwd):/backup alpine \
  tar czf /backup/dronevault-backup-$(date +%F).tar.gz /data

# Restore
docker run --rm -v dronevault-data:/data -v $(pwd):/backup alpine \
  tar xzf /backup/dronevault-backup-YYYY-MM-DD.tar.gz -C /
```
