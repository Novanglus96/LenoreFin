# develop stage
FROM node:lts-alpine AS develop-stage
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .

# build stage
FROM develop-stage AS build-stage
RUN npm run build

# Set timezone
RUN apk add -U tzdata
ENV TZ=America/New_York
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ >/etc/timezone

# production stage
FROM nginx:stable-alpine AS production-stage
LABEL maintainer="John Adams"
LABEL version="1.0.0"
COPY --from=build-stage /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
