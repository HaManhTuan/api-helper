# Ubuntu Production Deployment (Docker Compose)

This guide helps you deploy the project on a fresh Ubuntu server with minimal steps.

## 1) Server prerequisites

Install Docker Engine + Docker Compose plugin:

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

Optional (run docker without sudo):

```bash
sudo usermod -aG docker "$USER"
newgrp docker
```

## 2) Prepare project

```bash
git clone <your-repo-url>
cd api-helper-fast
cp .env.prod.example .env.prod
```

Edit `.env.prod` and replace all sensitive defaults:

- `POSTGRES_PASSWORD`
- `JWT_SECRET_KEY`
- any other production-specific value

## 3) Deploy

```bash
make prod-deploy
```

This command will:

1. Build production images
2. Start stack in detached mode
3. Run Alembic migrations
4. Seed default data

## 4) Verify services

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml ps
docker compose --env-file .env.prod -f docker-compose.prod.yml logs -f --tail=200
```

API default endpoint:

- `http://<server-ip>:8000/health`

## 5) Day-2 operations

```bash
make prod-build
make prod-up
make prod-logs
make prod-down
```

## 6) Recommended hardening before public traffic

- Put Nginx/Caddy in front and expose only `80/443`.
- Restrict inbound firewall rules (`ufw`).
- Keep `.env.prod` out of git.
- Rotate secrets regularly.
