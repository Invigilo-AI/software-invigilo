# Stage 0, "build-stage", based on Node.js, to build and compile the frontend
FROM bitnami/node:14 AS build-stage
WORKDIR /app

COPY package.json /app/
COPY yarn.lock /app/
RUN CYPRESS_INSTALL_BINARY=0 yarn --frozen-lockfile

COPY ./ /app/

ARG FRONTEND_ENV=production

ENV VUE_APP_ENV=${FRONTEND_ENV}

# Comment out the next line to disable tests
# RUN npm run test:unit

RUN SILENT=1 yarn run build


# Stage 1, based on Nginx, to have only the compiled app, ready for production with Nginx

# FROM bitnami/node:14-prod AS prod
# WORKDIR /app

# COPY --from=build /app .

# EXPOSE 5000 8080

# CMD ["yarn", "preview"]

FROM nginx:1.21 AS prod

WORKDIR /app

COPY --from=build-stage /app/dist/ /app
# COPY --from=build-stage /app/dist/ /usr/share/nginx/html

# COPY ./nginx/default.conf /etc/nginx/conf.d/default.conf
COPY ./nginx/vuejs.conf /etc/nginx/conf.d/default.conf
# COPY ./nginx/nginx-backend-not-found.conf /etc/nginx/extra-conf.d/backend-not-found.conf
