###########
# STAGE 1 #
# Vue build
###########
FROM node:lts-alpine AS frontend-build

WORKDIR /app
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

###########
# STAGE 2 #
# Python wheels
###########
FROM python:3.11.4-slim-bookworm AS backend-builder

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
FROM python:3.11.4-slim-bookworm

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
RUN pip install --upgrade pip && pip install --no-cache /wheels/*

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
