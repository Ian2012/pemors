build:
	docker-compose -f local.yml build

run:
	docker-compose -f local.yml up

migrate:
	docker-compose -f local.yml run --rm django python manage.py migrate
