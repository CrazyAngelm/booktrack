FROM python:3.11-slim-bullseye AS base
WORKDIR /app

RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential \
 && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy only pyproject.toml & lockfile for caching
COPY pyproject.toml poetry.lock ./

# Tell Poetry not to create a venv and install all deps (including dev)
RUN poetry config virtualenvs.create false \
 && poetry install --no-root --no-interaction --no-ansi

# Copy the rest of the code
COPY . .

RUN chmod +x run_frontend.sh

EXPOSE 8501

CMD ["/bin/sh", "run_frontend.sh"]
