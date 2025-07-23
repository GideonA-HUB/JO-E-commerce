from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile
from django.db.models import Count

class Command(BaseCommand):
    help = 'Remove duplicate users with the same email, keeping only the most recently created user for each email.'

    def handle(self, *args, **options):
        duplicates = (
            User.objects.values('email')
            .annotate(email_count=Count('id'))
            .filter(email_count__gt=1)
        )
        total_removed = 0
        for entry in duplicates:
            email = entry['email']
            users = User.objects.filter(email__iexact=email).order_by('-date_joined', '-id')
            users_to_keep = users[:1]
            users_to_remove = users[1:]
            for user in users_to_remove:
                # Remove related UserProfile if exists
                try:
                    profile = user.profile
                    profile.delete()
                except UserProfile.DoesNotExist:
                    pass
                user.delete()
                total_removed += 1
                self.stdout.write(self.style.WARNING(f'Removed duplicate user: {user.email} (id={user.id})'))
            if users_to_remove:
                self.stdout.write(self.style.SUCCESS(f'Kept user: {users_to_keep[0].email} (id={users_to_keep[0].id})'))
        if total_removed == 0:
            self.stdout.write(self.style.SUCCESS('No duplicate users found.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Removed {total_removed} duplicate users.')) 