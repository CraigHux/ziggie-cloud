# Ziggie SSL/TLS Quick Reference

> One-page reference for common SSL operations on ziggie.cloud

---

## DNS Records (Hostinger)

Add these A records at hpanel.hostinger.com > Domains > ziggie.cloud > DNS:

| Name | Type | Value |
|------|------|-------|
| @ | A | YOUR_VPS_IP |
| api | A | YOUR_VPS_IP |
| n8n | A | YOUR_VPS_IP |
| grafana | A | YOUR_VPS_IP |
| portainer | A | YOUR_VPS_IP |
| flowise | A | YOUR_VPS_IP |
| chat | A | YOUR_VPS_IP |
| mcp | A | YOUR_VPS_IP |
| sim | A | YOUR_VPS_IP |

---

## Initial SSL Setup

```bash
# SSH to VPS
ssh root@YOUR_VPS_IP

# Run setup script (test with --staging first)
cd /opt/ziggie
./scripts/setup-ssl.sh --staging

# If staging works, run production
./scripts/setup-ssl.sh
```

---

## Quick Commands

### Check Certificate Status

```bash
# All domains
./scripts/check-ssl.sh

# Single domain
echo | openssl s_client -servername ziggie.cloud -connect ziggie.cloud:443 2>/dev/null | openssl x509 -noout -dates

# Certbot view
docker run --rm -v /opt/ziggie/certbot/conf:/etc/letsencrypt:ro certbot/certbot certificates
```

### Force Renewal

```bash
./scripts/renew-ssl.sh --force
```

### Manual Certificate Request

```bash
docker run --rm -it \
  -v /opt/ziggie/certbot/conf:/etc/letsencrypt \
  -v /opt/ziggie/certbot/www:/var/www/certbot \
  certbot/certbot certonly \
    --webroot --webroot-path=/var/www/certbot \
    --email admin@ziggie.cloud --agree-tos --no-eff-email \
    -d ziggie.cloud -d api.ziggie.cloud -d n8n.ziggie.cloud
```

### Nginx Operations

```bash
# Test config
docker exec ziggie-nginx nginx -t

# Reload (no downtime)
docker exec ziggie-nginx nginx -s reload

# View logs
docker logs ziggie-nginx --tail 100
```

---

## File Locations

| File | Location |
|------|----------|
| Nginx HTTPS config | `/opt/ziggie/nginx/nginx.conf` |
| Certificates | `/opt/ziggie/certbot/conf/live/ziggie.cloud/` |
| Renewal log | `/var/log/ziggie-ssl-renewal.log` |
| Setup script | `/opt/ziggie/scripts/setup-ssl.sh` |
| Renewal script | `/opt/ziggie/scripts/renew-ssl.sh` |
| Check script | `/opt/ziggie/scripts/check-ssl.sh` |

---

## Cron Setup

```bash
crontab -e
# Add:
0 3,15 * * * /opt/ziggie/scripts/renew-ssl.sh >> /var/log/ziggie-ssl-renewal.log 2>&1
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Connection refused" | Check port 80/443 firewall: `ufw allow 80 && ufw allow 443` |
| "Too many certificates" | Wait 7 days or use `--staging` flag |
| "DNS not propagated" | Wait 5-15 min, verify with `dig ziggie.cloud` |
| HTTPS not working | Check nginx logs: `docker logs ziggie-nginx` |
| Cert not renewing | Check certbot: `docker logs ziggie-certbot` |

---

## Service URLs (After SSL Setup)

| Service | URL |
|---------|-----|
| Main | https://ziggie.cloud |
| API | https://api.ziggie.cloud |
| n8n | https://n8n.ziggie.cloud |
| Grafana | https://grafana.ziggie.cloud |
| Portainer | https://portainer.ziggie.cloud |
| Flowise | https://flowise.ziggie.cloud |
| Chat | https://chat.ziggie.cloud |
| MCP Gateway | https://mcp.ziggie.cloud |
| Sim Studio | https://sim.ziggie.cloud |

---

## SSL Labs Test

https://www.ssllabs.com/ssltest/analyze.html?d=ziggie.cloud

**Expected Grade: A or A+**

---

*Last Updated: 2025-12-28*
