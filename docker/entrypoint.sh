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
from webapp.models import Organization, UserOrganization, Catalogue, Dataset, DQAssessment
import os

admin_username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
admin_email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@quantum.local')
admin_password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')

# Create superuser
if not User.objects.filter(username=admin_username).exists():
    User.objects.create_superuser(admin_username, admin_email, admin_password)
    print(f'Superuser \"{admin_username}\" created successfully')
else:
    print(f'Superuser \"{admin_username}\" already exists')

# Create default organization
org, created = Organization.objects.get_or_create(name='Default Organization')
if created:
    print('Default organization created')
else:
    print('Default organization already exists')

# Associate admin with organization
user = User.objects.get(username=admin_username)
user_org, created = UserOrganization.objects.get_or_create(
    user=user,
    organization=org
)
if created:
    print(f'Admin user linked to organization')
else:
    print(f'Admin user already linked to organization')

# Create demo catalogue
demo_catalogue, created = Catalogue.objects.get_or_create(
    title='QUANTUM Demo Health Data Catalogue',
    defaults={
        'version': 1.0,
        'part_of': 'European Health Data Space (EHDS) Demo Environment',
        'fdp_id': 'demo-catalogue-001',
        'user': user
    }
)
if created:
    print('Demo catalogue created successfully')
else:
    print('Demo catalogue already exists')

# Create demo dataset with assessment
demo_assessment, created = DQAssessment.objects.get_or_create(
    defaults={
        'status': 'O',  # Ongoing
    }
)
if created:
    print('Demo assessment created')

demo_dataset, created = Dataset.objects.get_or_create(
    name='Sample European Health Dataset',
    defaults={
        'URI': 'https://demo.quantumproject.eu/datasets/sample-health-data-001',
        'description': 'A demonstration dataset showcasing health data quality assessment capabilities within the QUANTUM framework. This synthetic dataset contains anonymized health records designed to illustrate the data quality labeling process and compliance with HealthDCAT-AP standards.',
        'version': 1.0,
        'organization': org,
        'catalogue': demo_catalogue,
        'dq_assessment': demo_assessment,
        'fdp_id': 'demo-dataset-001'
    }
)
if created:
    print('Demo dataset created successfully')
else:
    print('Demo dataset already exists')
" 2>/dev/null || echo "Could not create/check superuser"

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
