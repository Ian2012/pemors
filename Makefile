build:
	docker-compose -f local.yml build

run:
	docker-compose -f local.yml up

migrate:
	docker-compose -f local.yml run --rm django python manage.py migrate

makemigrations:
	docker-compose -f local.yml run --rm django python manage.py createsuperuser

createsuperuser:
	docker-compose -f local.yml run --rm django python manage.py createsuperuser

train:
	docker-compose -f local.yml run --rm django python manage.py train
