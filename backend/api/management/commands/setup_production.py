from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.management import call_command

User = get_user_model()

class Command(BaseCommand):
    help = 'Set up production database with migrations and default superuser'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Setting up production database...')
        
        # Run migrations
        self.stdout.write('🗄️ Running migrations...')
        call_command('migrate')
        
        # Create default superuser
        self.stdout.write('👤 Creating default superuser...')
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@tastyfingers.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('✅ Default superuser created: admin/admin123'))
        else:
            self.stdout.write('ℹ️ Superuser already exists')
        
        # Collect static files
        self.stdout.write('📁 Collecting static files...')
        call_command('collectstatic', '--noinput')
        
        self.stdout.write(self.style.SUCCESS('✅ Production setup completed!'))
