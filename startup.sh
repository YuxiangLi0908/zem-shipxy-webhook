# #!/bin/bash

# export POETRY_HOME="/opt/poetry"
# export PATH="$POETRY_HOME/bin:$PATH"

# # Install poetry if not installed
# if [ ! -d "$POETRY_HOME" ]; then
#     curl -sSL https://install.python-poetry.org | python3 -
# fi

# cd /home/site/wwwroot

# # Install dependencies
# poetry install --no-interaction --no-root

# # Run FastAPI
# echo "Starting FastAPI with Uvicorn..."
# poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000

#!/bin/bash

echo "=== Startup script started ==="

# ----- 1. Configure Poetry to install venv inside project -----
export POETRY_VIRTUALENVS_IN_PROJECT=true
export POETRY_HOME="/opt/poetry"
export PATH="$POETRY_HOME/bin:$PATH"

APP_DIR="/home/site/wwwroot"
VENV_DIR="$APP_DIR/.venv"

cd $APP_DIR

# ----- 2. Install Poetry if not already installed -----
if [ ! -d "$POETRY_HOME" ]; then
    echo "Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
else
    echo "Poetry already installed."
fi

# Ensure poetry is in PATH
export PATH="$POETRY_HOME/bin:$PATH"

# ----- 3. Create Poetry venv + install dependencies -----
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating Poetry virtual environment and installing dependencies..."
    poetry install --no-interaction --no-root
else
    echo "Poetry venv already exists. Skipping installation."
    echo "Updating dependencies if needed..."
    poetry install --no-interaction --no-root --sync
fi

# ----- 4. Activate venv -----
source "$VENV_DIR/bin/activate"
echo "Using virtualenv at: $VENV_DIR"

# ----- 5. Start FastAPI server -----
echo "Starting FastAPI with Uvicorn..."
exec "$VENV_DIR/bin/uvicorn" app.main:app --host 0.0.0.0 --port 8000
