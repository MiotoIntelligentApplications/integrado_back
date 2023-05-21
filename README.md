# cargo_connect

pip install fastapi fastapi-sqlalchemy pydantic alembic psycopg2 uvicorn python-dotenv

alembic init alembic

docker-compose run app alembic revision --autogenerate -m "Initial Migration"
docker-compose run app alembic upgrade head

docker-compose build
docker-compose up