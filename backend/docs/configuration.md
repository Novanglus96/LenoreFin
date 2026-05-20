# Configuration

All configuration is done via environment variables in your `.env` file. The table below covers every supported variable.

## Django / Security

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | Yes | — | Django secret key. Use a long random string in production. |
| `DEBUG` | Yes | `0` | Set to `1` to enable Django debug mode. **Never use `1` in production.** |
| `DJANGO_ALLOWED_HOSTS` | Yes | — | Space-separated list of hostnames Django will serve (e.g. `localhost myserver.local`). |
| `CSRF_TRUSTED_ORIGINS` | Yes | — | Comma-separated list of origins trusted for CSRF (e.g. `https://finance.example.com`). |

## Database

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SQL_ENGINE` | Yes | — | Database backend. Use `django.db.backends.postgresql`. |
| `SQL_DATABASE` | Yes | — | PostgreSQL database name. |
| `SQL_USER` | Yes | — | PostgreSQL username. |
| `SQL_PASSWORD` | Yes | — | PostgreSQL password. |
| `SQL_HOST` | Yes | — | PostgreSQL hostname. Use `db` when running with the included Compose file. |
| `SQL_PORT` | Yes | `5432` | PostgreSQL port. |
| `DATABASE` | Yes | — | Set to `postgres`. Used by the startup script to wait for the database. |

## Superuser Bootstrap

These variables create the initial admin user on first startup. They are only used if no superuser exists yet.

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DJANGO_SUPERUSER_USERNAME` | Yes | — | Admin username. |
| `DJANGO_SUPERUSER_EMAIL` | Yes | — | Admin email. |
| `DJANGO_SUPERUSER_PASSWORD` | Yes | — | Admin password. Change this immediately after first login. |

## Application

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `VITE_API_KEY` | Yes | — | API key embedded into the frontend at build time. Must match the key you create in the admin panel under **Auth → API Keys**. |
| `TIMEZONE` | No | `UTC` | Server timezone (e.g. `America/New_York`). Affects scheduled tasks and date display. |

## Networking

The app listens on port `80` inside the container. Map it to any host port you like:

```yaml
ports:
  - "8080:80"   # host:container
```

To serve behind a reverse proxy (e.g. Nginx Proxy Manager, Traefik, Caddy), point the proxy to the container on port `80` and make sure `DJANGO_ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` include the public hostname.

## Volumes

| Volume | Purpose |
|--------|---------|
| `lenorefin_postgres` | PostgreSQL data |
| `lenorefin_static` | Django static files (CSS, JS) |
| `lenorefin_media` | User-uploaded files (attachments, exports) |
| `lenorefin_bkp` | Backup archives |

Back up `lenorefin_postgres` and `lenorefin_media` regularly to protect your financial data.
