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