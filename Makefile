# Local development
run:
	python manage.py runserver

migrate:
	python manage.py makemigrations
	python manage.py migrate

# Docker Production
docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-restart:
	docker-compose restart

docker-shell:
	docker-compose exec web python manage.py shell

docker-migrate:
	docker-compose exec web python manage.py migrate

docker-createsuperuser:
	docker-compose exec web python manage.py createsuperuser

docker-collectstatic:
	docker-compose exec web python manage.py collectstatic --noinput

# Order management
cancel-expired-orders:
	python manage.py cancel_expired_orders --hours=2

cancel-expired-orders-dry:
	python manage.py cancel_expired_orders --hours=2 --dry-run

docker-cancel-expired:
	docker-compose exec web python manage.py cancel_expired_orders --hours=2

docker-cancel-expired-dry:
	docker-compose exec web python manage.py cancel_expired_orders --hours=2 --dry-run

# Docker Development
dev-build:
	docker-compose -f docker-compose.dev.yml build

dev-up:
	docker-compose -f docker-compose.dev.yml up

dev-down:
	docker-compose -f docker-compose.dev.yml down

dev-logs:
	docker-compose -f docker-compose.dev.yml logs -f

# Cleanup
docker-clean:
	docker-compose down -v
	docker system prune -f

# Deploy
deploy:
	git pull
	docker-compose build
	docker-compose up -d
	docker-compose exec web python manage.py migrate --noinput
	docker-compose exec web python manage.py collectstatic --noinput

