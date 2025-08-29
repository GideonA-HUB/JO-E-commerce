from django.db import migrations

def update_categories(apps, schema_editor):
    Product = apps.get_model('api', 'Product')
    
    # Update existing products to new categories
    Product.objects.filter(category='finger-foods').update(category='daily-meals')
    Product.objects.filter(category='beverages').update(category='beverages-treats')
    Product.objects.filter(category='desserts').update(category='beverages-treats')

def reverse_update_categories(apps, schema_editor):
    Product = apps.get_model('api', 'Product')
    
    # Reverse the changes
    Product.objects.filter(category='daily-meals').update(category='finger-foods')
    Product.objects.filter(category='beverages-treats').update(category='beverages')

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_alter_productcomment_unique_together_and_more'),
    ]

    operations = [
        migrations.RunPython(update_categories, reverse_update_categories),
    ]
