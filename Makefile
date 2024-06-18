restart:
	poetry run docker container restart my_administrator-app-1

stop:
	poetry run docker stop my_administrator-app-1 my_administrator-ngrok-1 my_administrator-db-1 my_administrator-redis-1

start:
	poetry run docker start my_administrator-app-1 my_administrator-ngrok-1 my_administrator-db-1 my_administrator-redis-1

delete:
	poetry run docker rm my_administrator-app-1 my_administrator-ngrok-1 my_administrator-db-1 my_administrator-redis-1

delete-volumes:
	poetry run docker volume rm my_administrator_redis_data my_administrator_postgres_data
