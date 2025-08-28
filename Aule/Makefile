SHELL := /bin/bash

# Compute your user/group IDs dynamically so files created by containers are owned by you
UID := $(shell id -u)
GID := $(shell id -g)

DOCKER_COMPOSE := UID=$(UID) GID=$(GID) docker compose

.PHONY: up upd down stop restart ps logs logs-api logs-worker api-sh worker-sh db-sh fix-perms open-cover-letter build

## Build images (if you change Dockerfile/requirements.txt)
build:
	$(DOCKER_COMPOSE) build

## Start all services (build if needed)
up:
	$(DOCKER_COMPOSE) up --build

## Start in background (detached)
upd:
	$(DOCKER_COMPOSE) up --build -d

## Stop and remove containers
down:
	$(DOCKER_COMPOSE) down

## Stop without removing
stop:
	$(DOCKER_COMPOSE) stop

## Restart just the API service
restart:
	$(DOCKER_COMPOSE) restart api

## Show running services
ps:
	$(DOCKER_COMPOSE) ps

## Tail all logs
logs:
	$(DOCKER_COMPOSE) logs -f

## Tail API logs
logs-api:
	$(DOCKER_COMPOSE) logs -f api

## Tail worker logs
logs-worker:
	$(DOCKER_COMPOSE) logs -f worker

## Shell into API container
api-sh:
	$(DOCKER_COMPOSE) exec api bash -lc "bash || sh"

## Shell into worker container
worker-sh:
	$(DOCKER_COMPOSE) exec worker bash -lc "bash || sh"

## psql shell into DB (requires psql on host OR use docker exec)
db-sh:
	$(DOCKER_COMPOSE) exec db psql -U aule -d aule

## Fix permissions of the ./out directory (host side)
fix-perms:
	sudo chown -R $(UID):$(GID) out || true
	chmod -R a+r out || true
	chmod a+rx out || true

## Open the rendered cover letter (Linux or macOS)
open-cover-letter:
	xdg-open out/cover_letter.html 2>/dev/null || open out/cover_letter.html
