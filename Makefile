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

load_imdb:
	docker-compose -f local.yml run --rm django python manage.py update_db --new True

load_ratings:
	docker-compose -f local.yml run --rm django python manage.py load_ratings

quickstart:
	make migrate
	make load_imdb
	make load_ratings

shell:
	docker-compose -f local.yml run --rm django python manage.py shell


django-bash:
	docker exec -it pemors_local_django /bin/bash
