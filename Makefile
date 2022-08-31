build:
	docker-compose -f local.yml build

run:
	docker-compose -f local.yml up

migrate:
	docker-compose -f local.yml run --rm django python manage.py migrate

makemigrations:
	docker-compose -f local.yml run --rm django python manage.py makemigrations

createsuperuser:
	docker-compose -f local.yml run --rm django python manage.py createsuperuser

train:
	docker-compose -f local.yml run --rm django python manage.py train

update_new_db:
	docker-compose -f local.yml run --rm django python manage.py update_db --new true 2 3 4

load_ratings:
	docker-compose -f local.yml run --rm django python manage.py load_ratings
