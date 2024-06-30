# develop stage
FROM node:lts-alpine AS develop-stage
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .

# build stage
FROM develop-stage AS build-stage
RUN npm run build

# production stage
FROM nginx:stable-alpine AS production-stage
LABEL maintainer="John Adams"
LABEL version="1.0.0"
COPY --from=build-stage /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
