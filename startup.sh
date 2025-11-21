#!/bin/bash

export POETRY_HOME="/opt/poetry"
export PATH="$POETRY_HOME/bin:$PATH"

# Install poetry if not installed
if [ ! -d "$POETRY_HOME" ]; then
    curl -sSL https://install.python-poetry.org | python3 -
fi

cd /home/site/wwwroot

# Install dependencies
poetry install --no-interaction --no-root

# Run FastAPI
echo "Starting FastAPI with Uvicorn..."
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
