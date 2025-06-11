#!/bin/bash

# Exit on any error
set -e

echo "🚀 Starting Django application..."

# Wait for database to be ready
echo "⏳ Waiting for database..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "✅ Database is ready!"

# Wait for redis to be ready
echo "⏳ Waiting for Redis..."
while ! nc -z redis 6379; do
  sleep 0.1
done
echo "✅ Redis is ready!"

# Run migrations
echo "📊 Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if it doesn't exist
echo "👑 Creating superuser..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='admin@auction.com').exists():
    User.objects.create_superuser(
        email='admin@auction.com',
        password='admin123',
        first_name='Admin',
        last_name='User'
    )
    print('✅ Superuser created: admin@auction.com / admin123')
else:
    print('✅ Superuser already exists')
EOF

# Start the application
echo "🌟 Starting Django development server..."
if [ "$DEBUG" = "true" ]; then
    echo "🔥 Running in DEBUG mode"
    python manage.py runserver 0.0.0.0:7500
else
    echo "🚀 Running in PRODUCTION mode with Gunicorn"
    gunicorn back.wsgi:application --bind 0.0.0.0:7500 --workers 3
fi