# Requirements Stage
FROM python:3.10-slim as requirements-stage
WORKDIR /tmp

# Install Poetry and required plugins
RUN pip install poetry poetry-plugin-export

# Install git and system dependencies
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

# Copy and export requirements
COPY ./pyproject.toml ./poetry.lock* /tmp/
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# Final Stage
FROM python:3.10-slim
WORKDIR /code

# Install system dependencies (git required for pip install)
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy application files
COPY ./alembic /code/alembic
COPY ./alembic.ini /code
COPY ./run.py /code
