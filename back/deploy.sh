#!/bin/bash

echo "🚀 Starting production deployment..."

# Pull latest code
git pull origin main

# Stop existing containers
docker-compose down

# Build and start services
docker-compose up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Run migrations
echo "🔄 Running migrations..."
docker exec auction_backend python manage.py migrate

# Collect static files
echo "📦 Collecting static files..."
docker exec auction_backend python manage.py collectstatic --noinput

# Create superuser if needed
echo "👤 Checking admin user..."
docker exec auction_backend python manage.py shell << 'EOF'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='admin@auction.com').exists():
    User.objects.create_superuser(
        email='admin@auction.com',
        password='SecurePass123!',
        first_name='Admin',
        last_name='User'
    )
    print("✅ Admin user created")
else:
    print("✅ Admin user exists")
EOF

# Check services
docker-compose ps

echo "✅ Deployment complete!"
echo "🌐 Frontend: https://auction.pinealdevelopers.com"
echo "🔧 Backend API: https://auction.pinealdevelopers.com/api/"
echo "👨‍💼 Admin: https://auction.pinealdevelopers.com/admin/"