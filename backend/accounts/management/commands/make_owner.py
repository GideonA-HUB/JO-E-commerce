from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile

class Command(BaseCommand):
    help = 'Make a user an owner'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Email of the user to make owner')

    def handle(self, *args, **options):
        email = options['email']
        
        try:
            user = User.objects.get(email=email)
            profile = user.profile
            profile.role = 'owner'
            profile.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully made {email} an owner')
            )
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User with email {email} does not exist')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error: {e}')
            )
