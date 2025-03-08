#!/bin/bash

# Load environment variables from .env file
set -a
source .env
set +a

# Make sure required directories exist
mkdir -p static media staticfiles

# Apply migrations
echo "Applying migrations..."
python manage.py migrate

# Run the server with Daphne
echo "Starting Daphne server..."
daphne -b 127.0.0.1 -p 8000 back.asgi:application