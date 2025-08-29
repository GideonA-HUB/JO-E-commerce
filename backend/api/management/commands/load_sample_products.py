from django.core.management.base import BaseCommand
from api.models import Product

class Command(BaseCommand):
    help = 'Load sample products'

    def handle(self, *args, **options):
        products_data = [
            {
                'name': 'Chicken Wings',
                'description': 'Crispy fried chicken wings with special seasoning',
                'price': 15.99,
                'category': 'daily-meals',
                'image': 'https://images.unsplash.com/photo-1567620832904-9fc6debc209f?w=400'
            },
            {
                'name': 'Beef Sliders',
                'description': 'Mini beef burgers with cheese and special sauce',
                'price': 12.99,
                'category': 'daily-meals',
                'image': 'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400'
            },
            {
                'name': 'Chocolate Cake',
                'description': 'Rich chocolate cake with cream filling',
                'price': 8.99,
                'category': 'beverages-treats',
                'image': 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=400'
            },
            {
                'name': 'Fresh Juice',
                'description': 'Freshly squeezed orange juice',
                'price': 5.99,
                'category': 'beverages-treats',
                'image': 'https://images.unsplash.com/photo-1622597480248-ec889cbde4b5?w=400'
            },
            {
                'name': 'Ice Cream',
                'description': 'Vanilla ice cream with toppings',
                'price': 6.99,
                'category': 'beverages-treats',
                'image': 'https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=400'
            },
            {
                'name': 'French Fries',
                'description': 'Crispy golden french fries',
                'price': 7.99,
                'category': 'daily-meals',
                'image': 'https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=400'
            },
            {
                'name': 'Smoothie',
                'description': 'Fresh fruit smoothie',
                'price': 8.99,
                'category': 'beverages-treats',
                'image': 'https://images.unsplash.com/photo-1505252585461-04db1eb84625?w=400'
            },
            {
                'name': 'Coffee',
                'description': 'Freshly brewed coffee',
                'price': 4.99,
                'category': 'beverages-treats',
                'image': 'https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=400'
            },
            {
                'name': 'Pizza Slice',
                'description': 'Delicious pizza slice',
                'price': 9.99,
                'category': 'daily-meals',
                'image': 'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400'
            },
            {
                'name': 'Hot Dog',
                'description': 'Classic hot dog with toppings',
                'price': 6.99,
                'category': 'daily-meals',
                'image': 'https://images.unsplash.com/photo-1612392062122-9b2ebdc3694e?w=400'
            },
            {
                'name': 'Milkshake',
                'description': 'Creamy chocolate milkshake',
                'price': 7.99,
                'category': 'beverages-treats',
                'image': 'https://images.unsplash.com/photo-1572490122747-3968b75cc699?w=400'
            },
            {
                'name': 'Cheesecake',
                'description': 'New York style cheesecake',
                'price': 10.99,
                'category': 'beverages-treats',
                'image': 'https://images.unsplash.com/photo-1533134242443-d4fd215305ad?w=400'
            },
            {
                'name': 'Buddha Bowl',
                'description': 'Healthy grain bowl with vegetables and protein',
                'price': 18.99,
                'category': 'food-bowls',
                'image': 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400'
            },
            {
                'name': 'Poke Bowl',
                'description': 'Fresh fish bowl with rice and vegetables',
                'price': 22.99,
                'category': 'food-bowls',
                'image': 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400'
            },
        ]
        for prod in products_data:
            Product.objects.get_or_create(
                name=prod['name'],
                defaults=prod
            )
        self.stdout.write(self.style.SUCCESS('Sample products loaded successfully.')) 