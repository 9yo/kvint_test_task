test:
	@bash -c 'set -a; source deployment/.env.test; set +a; poetry run pytest'

start-server:
	poetry run python -m src.service

start-client:
	poetry run python -m src.client

start-rabbitmq:
	docker compose -f deployment/docker-compose.yml --env-file deployment/.env up rabbitmq -d

start-docker-demo:
	docker compose -f deployment/docker-compose.yml --env-file deployment/.env up

stop-docker-demo:
	docker compose -f deployment/docker-compose.yml --env-file deployment/.env down