#!/bin/bash

# Exit on any error
set -e

echo "Starting Django application setup..."

# Wait for database to be ready
echo "Waiting for database to be available..."
while ! nc -z $QUANTUM_DATABASE_HOST $QUANTUM_DATABASE_PORT; do
  echo "   Database not ready yet, waiting..."
  sleep 2
done
echo "Database is ready!"

# Wait a bit more to ensure database initialization is complete
sleep 5

# Run Django migrations
echo "Running Django migrations..."
python manage.py migrate --noinput

# Create superuser if it doesn't exist
echo "Setting up superuser..."
python manage.py shell -c "
from django.contrib.auth.models import User
import os

admin_username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
admin_email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@quantum.local')
admin_password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')

if not User.objects.filter(username=admin_username).exists():
    User.objects.create_superuser(admin_username, admin_email, admin_password)
    print(f'✅ Superuser \"{admin_username}\" created successfully')
else:
    print(f'ℹ️  Superuser \"{admin_username}\" already exists')
" 2>/dev/null || echo "Error: could not create/check superuser"

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Database setup complete!"

# Start the application
echo "Starting Django application server..."
if [ "$DJANGO_DEBUG" = "1" ]; then
    echo "Running in DEBUG mode with Django development server"
    exec python manage.py runserver 0.0.0.0:8000
else
    echo "Running in PRODUCTION mode with Gunicorn"
    exec gunicorn --bind 0.0.0.0:8000 --workers=3 --timeout=60 quantum.wsgi:application
fi
