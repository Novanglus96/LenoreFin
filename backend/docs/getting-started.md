# Installation

LenoreFin runs as a single Docker image bundling the frontend, backend, nginx, and task worker. You need Docker, Docker Compose, a PostgreSQL database, and a Redis instance — all provided by the included Compose file.

## Prerequisites

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Step 1 — Create a `.env` file

Create a `.env` file in the directory where you'll run Compose. Adjust all values for your environment:

```env
DEBUG=0
SECRET_KEY=change-me-to-a-long-random-string
DJANGO_ALLOWED_HOSTS=localhost
CSRF_TRUSTED_ORIGINS=http://localhost

SQL_ENGINE=django.db.backends.postgresql
SQL_DATABASE=lenorefin
SQL_USER=lenorefinuser
SQL_PASSWORD=somepassword
SQL_HOST=db
SQL_PORT=5432
DATABASE=postgres

DJANGO_SUPERUSER_PASSWORD=supervisorpassword
DJANGO_SUPERUSER_EMAIL=someone@somewhere.com
DJANGO_SUPERUSER_USERNAME=supervisor

VITE_API_KEY=someapikey
TIMEZONE=America/New_York

# Set to "true" to enable Contributions, Notes, and Calculator in the Planning menu
VITE_OPT_FEATURES=false
```

See [Configuration](configuration.md) for a full reference of all available variables.

## Step 2 — Create a `docker-compose.yml` file

```yaml
services:
  app:
    image: novanglus96/lenorefin:latest
    container_name: lenorefin
    command: /home/app/web/start.app.sh
    volumes:
      - lenorefin_static:/home/app/web/staticfiles
      - lenorefin_media:/home/app/web/mediafiles
      - lenorefin_bkp:/backups/
    ports:
      - "8080:80"
    depends_on:
      - db
      - redis
    networks:
      - lenorefin
    env_file:
      - ./.env
    environment:
      - DEBUG=0

  db:
    image: postgres:15
    container_name: lenorefin_db
    volumes:
      - lenorefin_postgres:/var/lib/postgresql/data/
      - lenorefin_bkp:/backups/
    networks:
      - lenorefin
    env_file:
      - ./.env
    environment:
      - TZ=UTC
      - POSTGRES_USER=${SQL_USER}
      - POSTGRES_PASSWORD=${SQL_PASSWORD}
      - POSTGRES_DB=${SQL_DATABASE}

  redis:
    image: redis:7-alpine
    container_name: lenorefin_redis
    command: ["redis-server", "--appendonly", "yes"]
    networks:
      - lenorefin
    restart: unless-stopped

networks:
  lenorefin:

volumes:
  lenorefin_postgres:
  lenorefin_static:
  lenorefin_media:
  lenorefin_bkp:
```

## Step 3 — Start the application

```bash
docker compose up -d
```

Open your browser at `http://localhost:8080`. Log in with the superuser credentials you set in `.env`.

---

## Migrating from pre-v1.4

Version 1.4 consolidates the old multi-container setup (`frontend`, `backend`, `worker`, `nginx`) into a single `app` container.

### 1. Back up your data

```bash
docker exec lenorefin_backend python manage.py export_user_data
```

Copy the backup file to a safe location before proceeding.

### 2. Stop old containers

```bash
docker compose down
```

### 3. Replace your `docker-compose.yml`

Use the new 3-service format above. Remove the old `frontend`, `backend`, `worker`, and `nginx` service definitions.

### 4. Update `.env`

Add the new variable if it isn't already present:

```env
VITE_OPT_FEATURES=false
```

### 5. Rename volumes (if needed)

The old setup used volume names ending in `_volume` (e.g. `lenorefin_postgres_data`). The new names drop that suffix. Migrate data if you want to preserve it:

```bash
docker run --rm \
  -v lenorefin_postgres_data:/from \
  -v lenorefin_postgres:/to \
  alpine sh -c "cp -av /from/. /to/"
```

Repeat for `lenorefin_static_volume` → `lenorefin_static` and `lenorefin_media_volume` → `lenorefin_media`.

Alternatively, restore from the backup you took in step 1 via **Admin → Backup & Restore** after the new stack is running.

### 6. Pull and start

```bash
docker compose pull
docker compose up -d
```

### 7. Verify

Open the app. Check **Admin → Version** to confirm you are on v1.4 or later.
