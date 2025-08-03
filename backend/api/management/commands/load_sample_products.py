from django.core.management.base import BaseCommand
from api.models import Product

class Command(BaseCommand):
    help = 'Load sample products for TASTY FINGERS'

    def handle(self, *args, **options):
        products = [
            {
                'name': 'Sauced Chicken Wings',
                'description': 'Crispy chicken wings tossed in our signature sauce blend',
                'price': 12.99,
                'category': 'finger-foods',
                'image': 'https://images.unsplash.com/photo-1567620832904-9fe5cf175643?auto=format&fit=crop&w=1000&q=80',
            },
            {
                'name': 'Turkey Sliders',
                'description': 'Mini turkey sandwiches with fresh vegetables and special sauce',
                'price': 15.99,
                'category': 'finger-foods',
                'image': 'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?auto=format&fit=crop&w=1000&q=80',
            },
            {
                'name': 'Layered Yogurt Parfait',
                'description': 'Greek yogurt layered with granola and fresh seasonal fruits',
                'price': 8.99,
                'category': 'desserts',
                'image': 'https://images.unsplash.com/photo-1488477181946-6428a0291777?auto=format&fit=crop&w=1000&q=80',
            },
            {
                'name': 'Berry Yogurt Drink',
                'description': 'Refreshing yogurt drink blended with mixed berries',
                'price': 6.99,
                'category': 'beverages',
                'image': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?auto=format&fit=crop&w=1000&q=80',
            },
            {
                'name': 'Chocolate Cake',
                'description': 'Rich chocolate cake with ganache frosting',
                'price': 24.99,
                'category': 'desserts',
                'image': 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=1000&q=80',
            },
            {
                'name': 'Mini Spring Rolls',
                'description': 'Crispy vegetable spring rolls with sweet chili sauce',
                'price': 10.99,
                'category': 'finger-foods',
                'image': 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?auto=format&fit=crop&w=1000&q=80',
            },
            {
                'name': 'Mango Yogurt Smoothie',
                'description': 'Creamy mango yogurt smoothie with tropical flavors',
                'price': 7.99,
                'category': 'beverages',
                'image': 'https://images.unsplash.com/photo-1505252585461-04db1eb84625?auto=format&fit=crop&w=1000&q=80',
            },
            {
                'name': 'Vanilla Cupcakes',
                'description': 'Fluffy vanilla cupcakes with buttercream frosting',
                'price': 18.99,
                'category': 'desserts',
                'image': 'https://images.unsplash.com/photo-1486427944299-d1955d23e34d?auto=format&fit=crop&w=1000&q=80',
            },
            {
                'name': 'Bacon Wrapped Dates',
                'description': 'Sweet dates wrapped in crispy bacon',
                'price': 13.99,
                'category': 'finger-foods',
                'image': 'https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=1000&q=80',
            },
            {
                'name': 'Green Tea Yogurt',
                'description': 'Refreshing green tea flavored yogurt drink',
                'price': 5.99,
                'category': 'beverages',
                'image': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?auto=format&fit=crop&w=1000&q=80',
            },
            {
                'name': 'Cheesecake Bites',
                'description': 'Mini cheesecake bites with berry compote',
                'price': 16.99,
                'category': 'desserts',
                'image': 'https://images.unsplash.com/photo-1533134242443-d4fd215305ad?auto=format&fit=crop&w=1000&q=80',
            },
            {
                'name': 'Stuffed Mushrooms',
                'description': 'Mushrooms stuffed with cream cheese and herbs',
                'price': 11.99,
                'category': 'finger-foods',
                'image': 'https://images.unsplash.com/photo-1518977676601-b53f82aba655?auto=format&fit=crop&w=1000&q=80',
            },
        ]
        for prod in products:
            Product.objects.get_or_create(
                name=prod['name'],
                defaults=prod
            )
        self.stdout.write(self.style.SUCCESS('Sample products loaded successfully.')) 