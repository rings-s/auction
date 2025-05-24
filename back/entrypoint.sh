#!/bin/sh

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Start Django development server
echo "Starting Django development server..."
python manage.py runserver 0.0.0.0:8000