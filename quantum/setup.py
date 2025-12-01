from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Setup database with migrations and initial data'

    def handle(self, *args, **options):
        self.stdout.write('Running migrations...')
        call_command('migrate', verbosity=1)
        
        self.stdout.write('Collecting static files...')
        call_command('collectstatic', interactive=False, verbosity=1)
        
        # Create superuser if needed
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write('Superuser created')
        
        self.stdout.write(self.style.SUCCESS('Database setup complete!'))