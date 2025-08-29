from django.db import migrations

def add_sides_addons_category(apps, schema_editor):
    # This migration is mainly for future use
    # The category is already added to the model choices
    pass

def reverse_add_sides_addons_category(apps, schema_editor):
    # No reverse operation needed
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_update_categories'),
    ]

    operations = [
        migrations.RunPython(add_sides_addons_category, reverse_add_sides_addons_category),
    ]
