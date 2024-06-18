restart:
	docker container restart my_administrator-app-1

stop:
	docker stop my_administrator-app-1 my_administrator-ngrok-1 my_administrator-db-1 my_administrator-redis-1

start:
	docker start my_administrator-app-1 my_administrator-ngrok-1 my_administrator-db-1 my_administrator-redis-1

delete:
	docker rm my_administrator-app-1 my_administrator-ngrok-1 my_administrator-db-1 my_administrator-redis-1

delete-volumes:
	docker volume rm my_administrator_redis_data my_administrator_postgres_data

update-dicts:
	docker exec my_administrator-app-1 python app/database/insert_dicts/update_dicts.py

insert-dicts:
	docker exec my_administrator-app-1 python app/database/insert_dicts/insert_dicts.py

insert-users:
	docker exec my_administrator-app-1 python app/database/db_helpers/insert_users.py

