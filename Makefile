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
