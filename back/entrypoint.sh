#!/bin/bash

echo "🚀 Starting Django application..."

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL..."
while ! nc -z db 5432; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done
echo "✅ PostgreSQL is up and running!"

# Wait for Redis to be ready
echo "⏳ Waiting for Redis..."
while ! nc -z redis 6379; do
  echo "Redis is unavailable - sleeping"
  sleep 1
done
echo "✅ Redis is up and running!"

# Create cache table for database cache
echo "📦 Creating cache table..."
python manage.py createcachetable || echo "Cache table already exists or using Redis cache"

# Run database migrations
echo "🔄 Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if it doesn't exist
echo "👤 Creating superuser..."
python manage.py shell << 'EOF'
from django.contrib.auth import get_user_model
import os

User = get_user_model()

# Create superuser with environment variables or defaults
superuser_email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@auction.com')
superuser_password = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'SecurePass123!')
superuser_first_name = os.getenv('DJANGO_SUPERUSER_FIRST_NAME', 'Admin')
superuser_last_name = os.getenv('DJANGO_SUPERUSER_LAST_NAME', 'User')

if not User.objects.filter(email=superuser_email).exists():
    User.objects.create_superuser(
        email=superuser_email,
        password=superuser_password,
        first_name=superuser_first_name,
        last_name=superuser_last_name,
        is_staff=True,
        is_superuser=True
    )
    print(f"✅ Superuser created: {superuser_email}")
else:
    print(f"✅ Superuser already exists: {superuser_email}")
EOF

# Start the Django development server
echo "🔥 Starting Django server..."
if [ "$DEBUG" = "true" ]; then
    echo "🛠️  Running in DEBUG mode"
    python manage.py runserver 0.0.0.0:8000
else
    echo "🚀 Running in PRODUCTION mode with Gunicorn"
    gunicorn back.wsgi:application --bind 0.0.0.0:8000 --workers 3
fi