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

# Load demo data conditionally (enabled by default)
load_demo_data = os.environ.get('QUANTUM_LOAD_DEMO_DATA', '1').lower() in ('1', 'true', 'yes', 'on')

if load_demo_data:
    print('Loading demo data...')

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

    # Create additional demo catalogue for variety
    clinical_catalogue, created = Catalogue.objects.get_or_create(
        title='Clinical Research Data Catalogue',
        defaults={
            'version': 2.1,
            'part_of': 'Multi-center Clinical Trial Repository',
            'fdp_id': 'clinical-catalogue-002',
            'user': user
        }
    )
    if created:
        print('Clinical catalogue created successfully')

    # Create second demo dataset with different characteristics
    clinical_assessment, created = DQAssessment.objects.get_or_create(
        defaults={
            'status': 'V',  # Validated
        }
    )

    clinical_dataset, created = Dataset.objects.get_or_create(
        name='Cardiovascular Clinical Trial Dataset',
        defaults={
            'URI': 'https://demo.quantumproject.eu/datasets/cardio-trial-cv2025',
            'description': 'Multi-center cardiovascular clinical trial dataset (2020-2024) with comprehensive patient demographics, biomarkers, imaging data, and outcomes. Demonstrates high-quality data with complete documentation and validation procedures.',
            'version': 2.3,
            'organization': org,
            'catalogue': clinical_catalogue,
            'dq_assessment': clinical_assessment,
            'fdp_id': 'clinical-dataset-002'
        }
    )
    if created:
        print('Clinical dataset created successfully')

    # Create third dataset showing different maturity levels
    registry_assessment, created = DQAssessment.objects.get_or_create(
        defaults={
            'status': 'O',  # Ongoing
        }
    )

    registry_dataset, created = Dataset.objects.get_or_create(
        name='National Cancer Registry Extract',
        defaults={
            'URI': 'https://demo.quantumproject.eu/datasets/cancer-registry-2024',
            'description': 'Population-based cancer registry data extract covering major cancer types with diagnostic, treatment, and survival information. Includes quality metrics for completeness, accuracy, and timeliness of reporting.',
            'version': 1.5,
            'organization': org,
            'catalogue': demo_catalogue,
            'dq_assessment': registry_assessment,
            'fdp_id': 'registry-dataset-003'
        }
    )
    if created:
        print('Registry dataset created successfully')

    print('Demo data setup completed!')
    print('- Ready for complete workflow testing')
else:
    print('Demo data loading disabled via QUANTUM_LOAD_DEMO_DATA environment variable')
    print('Set QUANTUM_LOAD_DEMO_DATA=1 to enable demo data loading')

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
