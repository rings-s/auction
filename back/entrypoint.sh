#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

echo_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

echo_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Wait for database to be ready (if using PostgreSQL)
wait_for_db() {
    if [ "$DB_HOST" ]; then
        echo_info "Waiting for database at $DB_HOST:${DB_PORT:-5432}..."
        while ! nc -z "$DB_HOST" "${DB_PORT:-5432}"; do
            echo_warn "Database not ready, waiting..."
            sleep 2
        done
        echo_info "Database is ready!"
    fi
}

# Check required environment variables
check_env() {
    local required_vars=("SECRET_KEY")
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            echo_error "Required environment variable $var is not set"
            exit 1
        fi
    done
    echo_info "Environment variables check passed"
}

# Collect static files
collect_static() {
    echo_info "Collecting static files..."
    python manage.py collectstatic --noinput --clear
    echo_info "Static files collected successfully"
}

# Apply database migrations
migrate_db() {
    echo_info "Checking for database migrations..."
    python manage.py makemigrations --check --dry-run || {
        echo_warn "Unapplied migrations found, applying them..."
        python manage.py makemigrations
    }
    
    echo_info "Applying database migrations..."
    python manage.py migrate --noinput
    echo_info "Database migrations completed"
}

# Create superuser if needed
create_superuser() {
    if [ "$DJANGO_SUPERUSER_EMAIL" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ]; then
        echo_info "Creating superuser..."
        python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='$DJANGO_SUPERUSER_EMAIL').exists():
    User.objects.create_superuser(
        email='$DJANGO_SUPERUSER_EMAIL',
        password='$DJANGO_SUPERUSER_PASSWORD',
        first_name='Admin',
        last_name='User'
    )
    print('Superuser created successfully')
else:
    print('Superuser already exists')
EOF
    fi
}

# Main execution
main() {
    echo_info "Starting Django application setup..."
    
    # Environment checks
    check_env
    
    # Wait for dependencies
    wait_for_db
    
    # Database setup
    migrate_db
    
    # Static files (in production)
    if [ "$ENVIRONMENT" = "production" ]; then
        collect_static
    fi
    
    # Create superuser if specified
    create_superuser
    
    # Start the application
    echo_info "Starting Django application..."
    
    if [ "$ENVIRONMENT" = "production" ]; then
        echo_info "Starting Gunicorn server..."
        exec gunicorn back.asgi:application \
            --bind 0.0.0.0:8000 \
            --workers ${GUNICORN_WORKERS:-3} \
            --worker-class uvicorn.workers.UvicornWorker \
            --access-logfile - \
            --error-logfile - \
            --log-level info \
            --timeout 120 \
            --keep-alive 2 \
            --max-requests 1000 \
            --max-requests-jitter 100
    else
        echo_info "Starting Django development server..."
        exec python manage.py runserver 0.0.0.0:8000
    fi
}

# Handle signals
trap 'echo_info "Shutting down gracefully..."; exit 0' TERM INT

# Run main function
main "$@"