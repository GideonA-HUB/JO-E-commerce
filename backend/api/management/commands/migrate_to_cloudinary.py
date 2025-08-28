from django.core.management.base import BaseCommand
from django.conf import settings
from api.models import Product, CateringService, BlogPost
from api.cloudinary_service import cloudinary_service

class Command(BaseCommand):
    help = 'Migrate local images to Cloudinary'

    def add_arguments(self, parser):
        parser.add_argument(
            '--models',
            nargs='+',
            type=str,
            help='Specific models to migrate (product, catering, blog)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be migrated without actually doing it',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Starting Cloudinary migration...')
        )

        # Check if Cloudinary is configured
        if not all([
            settings.CLOUDINARY.get('cloud_name'),
            settings.CLOUDINARY.get('api_key'),
            settings.CLOUDINARY.get('api_secret')
        ]):
            self.stdout.write(
                self.style.ERROR('❌ Cloudinary not properly configured!')
            )
            self.stdout.write('Please set CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, and CLOUDINARY_API_SECRET')
            return

        models_to_migrate = []
        
        if options['models']:
            for model_name in options['models']:
                if model_name.lower() == 'product':
                    models_to_migrate.append((Product, 'image'))
                elif model_name.lower() == 'catering':
                    models_to_migrate.append((CateringService, 'image'))
                elif model_name.lower() == 'blog':
                    models_to_migrate.append((BlogPost, 'image'))
        else:
            # Migrate all models
            models_to_migrate = [
                (Product, 'image'),
                (CateringService, 'image'),
                (BlogPost, 'image'),
            ]

        total_success = 0
        total_failed = 0

        for model_class, image_field in models_to_migrate:
            self.stdout.write(
                f'\n📁 Migrating {model_class.__name__} images...'
            )

            if options['dry_run']:
                # Count what would be migrated
                count = model_class.objects.filter(
                    **{f"{image_field}__isnull": False}
                ).exclude(
                    **{f"{image_field}": ""}
                ).count()
                
                self.stdout.write(
                    f'   Would migrate {count} {model_class.__name__} images'
                )
                continue

            # Perform actual migration
            results = cloudinary_service.migrate_local_images(
                model_class, 
                image_field
            )

            total_success += results['success']
            total_failed += results['failed']

            self.stdout.write(
                self.style.SUCCESS(f'   ✅ Successfully migrated: {results["success"]}')
            )
            
            if results['failed'] > 0:
                self.stdout.write(
                    self.style.WARNING(f'   ❌ Failed to migrate: {results["failed"]}')
                )
                
                for error in results['errors'][:5]:  # Show first 5 errors
                    self.stdout.write(f'      - {error}')
                
                if len(results['errors']) > 5:
                    self.stdout.write(f'      ... and {len(results["errors"]) - 5} more errors')

        if not options['dry_run']:
            self.stdout.write(
                f'\n🎉 Migration completed!'
            )
            self.stdout.write(
                f'   Total successful: {total_success}'
            )
            self.stdout.write(
                f'   Total failed: {total_failed}'
            )
        else:
            self.stdout.write(
                f'\n📋 Dry run completed. No changes made.'
            )

        self.stdout.write(
            self.style.SUCCESS('\n✅ Cloudinary migration process finished!')
        )
