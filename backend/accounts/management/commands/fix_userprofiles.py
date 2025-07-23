from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile

class Command(BaseCommand):
    help = 'Create UserProfile for all users who do not have one'

    def handle(self, *args, **options):
        created = 0
        for user in User.objects.all():
            if not hasattr(user, 'profile'):
                role = 'owner' if user.is_superuser else 'staff'
                UserProfile.objects.create(user=user, role=role)
                self.stdout.write(self.style.SUCCESS(f'Created profile for {user.email} ({role})'))
                created += 1
        if created == 0:
            self.stdout.write(self.style.SUCCESS('All users already have profiles!'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Created {created} missing profiles.')) 