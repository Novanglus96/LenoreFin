###########
# STAGE 1 #
# Vue build
###########
# Digest-pinned on purpose. `node:lts-alpine` is fully floating — `lts` rolls to
# a new major on its own schedule — so rebuilding an OLD release tag could pull
# a different Node major and produce a materially different frontend bundle
# under the same version tag. That defeats "re-run any step after an outage with
# no gaps": the re-run would succeed and quietly ship different bytes.
#
# The Python bases below are pinned the same way, by version and digest. They
# were python:3.11.4-slim-bookworm from 2023 until 2026-11-23, which carried
# ~1,500 fixed-upstream OS CVEs; bumping the base is how those get fixed.
# Stay on bookworm while the database is Postgres 15: its postgresql-client is
# what the backups run with, and pg_dump must not be older than the server.
# To bump: docker pull python:3.11-slim-bookworm && docker image inspect \
#            python:3.11-slim-bookworm --format '{{index .RepoDigests 0}}'
# (python 3.11.18, Debian 12.15 as of 2026-11-23)
#
# To bump: docker pull node:lts-alpine && docker image inspect node:lts-alpine \
#            --format '{{index .RepoDigests 0}}'
# and update the comment with the version you moved to.
FROM node:lts-alpine@sha256:d32cdf619f63fe0471182d08996dd516c6275bb5fd31ae06e55a570bd9e1ad43 AS frontend-build
# ^ node 24.19.0 (lts-alpine as of 2026-08-07)

WORKDIR /app
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

###########
# STAGE 2 #
# Python wheels
###########
FROM python:3.11.18-slim-bookworm@sha256:a83ba18aef0f865b1a4a611c2cf460fe446f2795673bbb9fe43be570439e3b39 AS backend-builder

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends gcc

RUN pip install --upgrade pip
RUN pip install flake8==6.0.0
COPY backend/ /usr/src/app/
RUN flake8 --ignore=E501,F401,E203,E701,W503 ./backend

COPY backend/requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt

###########
# STAGE 3 #
# Final single-container image
###########
FROM python:3.11.18-slim-bookworm@sha256:a83ba18aef0f865b1a4a611c2cf460fe446f2795673bbb9fe43be570439e3b39

LABEL maintainer="John Adams"

# Install nginx, supervisord, and runtime deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    supervisor \
    netcat-openbsd \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir -p $APP_HOME/staticfiles $APP_HOME/mediafiles $APP_HOME/logs
RUN mkdir -p /backups
WORKDIR $APP_HOME

# Python dependencies
COPY --from=backend-builder /usr/src/app/wheels /wheels
COPY --from=backend-builder /usr/src/app/requirements.txt .
# setuptools ships with the base image at 70.3.0, which (with the jaraco.context
# and wheel it vendors) carries fixed HIGH CVEs. Pinned like the base.
RUN pip install --upgrade pip setuptools==84.2.1 && pip install --no-cache /wheels/*

# Vue static files
COPY --from=frontend-build /app/dist /usr/share/nginx/html

# Backend static assets
COPY backend/logos/logov2.png $APP_HOME/staticfiles/logov2.png
COPY backend/logos/favicon.ico $APP_HOME/staticfiles/favicon.ico

# Backend app
COPY backend/ $APP_HOME/

# Scripts
RUN sed -i 's/\r$//g' $APP_HOME/entrypoint.sh && chmod +x $APP_HOME/entrypoint.sh
RUN sed -i 's/\r$//g' $APP_HOME/start.app.sh && chmod +x $APP_HOME/start.app.sh

# Nginx config
COPY nginx/app.conf /etc/nginx/conf.d/default.conf
RUN rm -f /etc/nginx/sites-enabled/default

# Supervisord config
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 80

ENTRYPOINT ["/home/app/web/entrypoint.sh"]
CMD ["/home/app/web/start.app.sh"]
