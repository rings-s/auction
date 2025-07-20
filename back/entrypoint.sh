#!/bin/bash

# Exit on any error
set -e

echo "🚀 Starting Django application..."

# Wait for database to be ready with exponential backoff
echo "⏳ Waiting for database..."
wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3
    local max_attempts=30
    local attempt=1
    local sleep_time=1

    while [ $attempt -le $max_attempts ]; do
        if nc -z $host $port; then
            echo "✅ $service_name is ready!"
            return 0
        fi
        echo "⏳ Waiting for $service_name... (attempt $attempt/$max_attempts)"
        sleep $sleep_time
        attempt=$((attempt + 1))
        sleep_time=$((sleep_time > 8 ? 8 : sleep_time * 2))
    done
    
    echo "❌ Failed to connect to $service_name after $max_attempts attempts"
    exit 1
}

wait_for_service "db" "5432" "database"
wait_for_service "redis" "6379" "Redis"

# Run migrations only if needed
echo "📊 Checking database migrations..."
if python manage.py showmigrations --plan | grep -q '\[ \]'; then
    echo "📊 Running database migrations..."
    python manage.py makemigrations
    python manage.py migrate
else
    echo "✅ Database migrations up to date"
fi

# Create cache table for database cache backend
echo "🗄️ Creating cache table..."
python manage.py createcachetable cache_table || echo "Cache table already exists or using different cache backend"

# Collect static files only if needed
echo "📦 Checking static files..."
if [ ! -d "/app/staticfiles" ] || [ -z "$(ls -A /app/staticfiles)" ]; then
    echo "📦 Collecting static files..."
    python manage.py collectstatic --noinput
else
    echo "✅ Static files already collected"
fi

# Create superuser if it doesn't exist using environment variables
echo "👑 Creating superuser..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
import os

User = get_user_model()
admin_email = os.getenv('ADMIN_EMAIL', 'admin@auction.com')
admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')

if not User.objects.filter(email=admin_email).exists():
    User.objects.create_superuser(
        email=admin_email,
        password=admin_password,
        first_name='Admin',
        last_name='User'
    )
    print(f'✅ Superuser created: {admin_email}')
else:
    print(f'✅ Superuser already exists: {admin_email}')
EOF

# Start the application
echo "🌟 Starting Django development server..."
if [ "$DEBUG" = "true" ]; then
    echo "🔥 Running in DEBUG mode"
    python manage.py runserver 0.0.0.0:8000
else
    echo "🚀 Running in PRODUCTION mode with Gunicorn"
    gunicorn back.wsgi:application --bind 0.0.0.0:8000 --workers 3
fi