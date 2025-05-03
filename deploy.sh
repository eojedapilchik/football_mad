#!/bin/bash

# Config
PROJECT_DIR="/home/automation/service"
VENV_DIR="$PROJECT_DIR/venv"
SERVICE_NAME="fastapi"
DOCKER_COMPOSE_FILE="$PROJECT_DIR/docker-compose.yml"

echo ">>> Pulling latest code..."
if [ ! -d "$PROJECT_DIR" ]; then
    echo "Error: Project directory $PROJECT_DIR does not exist."
    exit 1
fi
cd $PROJECT_DIR || { echo "Error: Failed to change directory to $PROJECT_DIR"; exit 1; }
git pull

echo ">>> Activating virtual environment and installing requirements..."
source $VENV_DIR/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate

echo ">>> Restarting the service..."
sudo systemctl restart $SERVICE_NAME

echo ">>> Stopping Docker Compose services..."
docker compose -f "$DOCKER_COMPOSE_FILE" down

export COMPOSE_BAKE=true

echo ">>> Building Docker Compose services using Bake..."
docker compose -f "$DOCKER_COMPOSE_FILE" build

echo ">>> Starting Docker Compose services..."
docker compose -f "$DOCKER_COMPOSE_FILE" up -d

echo ">>> Restarting the system service ($SERVICE_NAME)..."
sudo systemctl restart "$SERVICE_NAME"

echo ">>> Deployment finished!"
