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

# Wait for database to be ready with better error handling
wait_for_db() {
    if [ "$DB_HOST" ]; then
        echo_info "Waiting for database at $DB_HOST:${DB_PORT:-5432}..."
        local max_attempts=30
        local attempt=1
        
        while [ $attempt -le $max_attempts ]; do
            if nc -z "$DB_HOST" "${DB_PORT:-5432}"; then
                echo_info "Database is ready!"
                return 0
            else
                echo_warn "Database not ready, attempt $attempt/$max_attempts"
                sleep 2
                ((attempt++))
            fi
        done
        
        echo_error "Database connection failed after $max_attempts attempts"
        exit 1
    else
        echo_info "No database host specified, skipping database check"
    fi
}

# Enhanced environment check
check_env() {
    local required_vars=("SECRET_KEY")
    local missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        echo_error "Missing required environment variables: ${missing_vars[*]}"
        exit 1
    fi
    
    # Check database variables if DB_HOST is set
    if [ "$DB_HOST" ]; then
        local db_vars=("DB_NAME" "DB_USER" "DB_PASSWORD")
        for var in "${db_vars[@]}"; do
            if [ -z "${!var}" ]; then
                missing_vars+=("$var")
            fi
        done
        
        if [ ${#missing_vars[@]} -ne 0 ]; then
            echo_error "Missing database environment variables: ${missing_vars[*]}"
            exit 1
        fi
    fi
    
    echo_info "Environment variables check passed"
}

# Collect static files with error handling
collect_static() {
    echo_info "Collecting static files..."
    if python manage.py collectstatic --noinput --clear; then
        echo_info "Static files collected successfully"
    else
        echo_error "Failed to collect static files"
        exit 1
    fi
}

# Apply database migrations with better error handling
migrate_db() {
    echo_info "Checking for database migrations..."
    
    # Check if we can connect to database
    if ! python manage.py check --database default; then
        echo_error "Database connection failed"
        exit 1
    fi
    
    # Make migrations if needed
    if ! python manage.py makemigrations --check --dry-run >/dev/null 2>&1; then
        echo_warn "Creating new migrations..."
        python manage.py makemigrations
    fi
    
    # Apply migrations
    echo_info "Applying database migrations..."
    if python manage.py migrate --noinput; then
        echo_info "Database migrations completed"
    else
        echo_error "Database migration failed"
        exit 1
    fi
}

# Create superuser if needed
create_superuser() {
    if [ "$DJANGO_SUPERUSER_EMAIL" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ]; then
        echo_info "Creating superuser..."
        python manage.py shell << EOF
import os
from django.contrib.auth import get_user_model
try:
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
except Exception as e:
    print(f'Error creating superuser: {e}')
    exit(1)
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
    
    # Static files (in production or if explicitly requested)
    if [ "$ENVIRONMENT" = "production" ] || [ "$COLLECT_STATIC" = "true" ]; then
        collect_static
    fi
    
    # Create superuser if specified
    create_superuser
    
    # Start the application
    echo_info "Starting Django application..."
    
    if [ "$ENVIRONMENT" = "production" ]; then
        echo_info "Starting Gunicorn server..."
        exec gunicorn back.asgi:application \
            --bind 0.0.0.0:7500 \
            --workers ${GUNICORN_WORKERS:-3} \
            --worker-class uvicorn.workers.UvicornWorker \
            --access-logfile - \
            --error-logfile - \
            --log-level ${LOG_LEVEL:-info} \
            --timeout 120 \
            --keep-alive 2 \
            --max-requests 1000 \
            --max-requests-jitter 100 \
            --preload
    else
        echo_info "Starting Django development server..."
        exec python manage.py runserver 0.0.0.0:7500
    fi
}

# Handle signals gracefully
cleanup() {
    echo_info "Received shutdown signal, cleaning up..."
    # Add any cleanup operations here
    exit 0
}

trap cleanup TERM INT

# Run main function
main "$@"