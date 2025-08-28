SHELL := /bin/bash

# Use names that won't collide with bash's readonly UID variable
USER_ID := $(shell id -u)
GROUP_ID := $(shell id -g)

DOCKER_COMPOSE := sudo USER_ID=$(USER_ID) GROUP_ID=$(GROUP_ID) docker compose

.PHONY: up upd down stop restart ps logs logs-api logs-worker api-sh worker-sh db-sh fix-perms open-cover-letter build render-letter

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

## Render a sample cover letter HTML inside the API container
render-letter:
	$(DOCKER_COMPOSE) exec api python scripts/render_letter.py
	@$(MAKE) fix-perms

## Open the rendered cover letter using Python (works without sudo)
open-cover-letter:
	python - <<'PY'
	import webbrowser, pathlib, sys
	p = pathlib.Path("out/cover_letter.html").resolve()
	if not p.exists():
		sys.exit("out/cover_letter.html not found. Run `make render-letter` first.")
	webbrowser.open(p.as_uri())
	print("Opened", p)
	PY