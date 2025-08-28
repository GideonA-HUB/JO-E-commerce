from django.core.management.base import BaseCommand
from api.models import Product, Category
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Add sample data to the database'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Adding sample data...')
        
        # Create superuser if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@tastyfingers.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('✅ Superuser created: admin/admin123'))
        
        # Create categories
        categories = [
            {'name': 'Finger Foods', 'slug': 'finger-foods'},
            {'name': 'Beverages', 'slug': 'beverages'},
            {'name': 'Desserts', 'slug': 'desserts'},
        ]
        
        for cat_data in categories:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={'name': cat_data['name']}
            )
            if created:
                self.stdout.write(f'✅ Created category: {category.name}')
        
        # Create sample products
        products_data = [
            {
                'name': 'Chicken Wings',
                'description': 'Crispy fried chicken wings with special seasoning',
                'price': 15.99,
                'category': 'finger-foods',
                'image': 'https://images.unsplash.com/photo-1567620832904-9fc6debc209f?w=400'
            },
            {
                'name': 'Beef Sliders',
                'description': 'Mini beef burgers with cheese and special sauce',
                'price': 12.99,
                'category': 'finger-foods',
                'image': 'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400'
            },
            {
                'name': 'Fresh Juice',
                'description': 'Freshly squeezed orange juice',
                'price': 5.99,
                'category': 'beverages',
                'image': 'https://images.unsplash.com/photo-1622597480248-ec889cbde4b5?w=400'
            },
            {
                'name': 'Chocolate Cake',
                'description': 'Rich chocolate cake with cream filling',
                'price': 8.99,
                'category': 'desserts',
                'image': 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=400'
            },
        ]
        
        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults={
                    'description': product_data['description'],
                    'price': product_data['price'],
                    'category': product_data['category'],
                    'image': product_data['image'],
                    'is_available': True
                }
            )
            if created:
                self.stdout.write(f'✅ Created product: {product.name}')
        
        self.stdout.write(self.style.SUCCESS('✅ Sample data added successfully!'))
