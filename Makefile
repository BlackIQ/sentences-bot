.PHONY: all
all: update down up

.PHONY: update
update:
	@echo "Update"
	git pull

.PHONY: up
up:
	@echo "Build & Up"
	docker compose -p quote up -d --build

.PHONY: down
down:
	@echo "Down"
	docker compose -p quote down
