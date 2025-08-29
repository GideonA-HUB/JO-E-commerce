from django.core.management.base import BaseCommand
from api.models import Product, Category, CateringService
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
            {'name': 'Daily Affordable Meals', 'slug': 'daily-meals'},
            {'name': 'Food Bowls', 'slug': 'food-bowls'},
            {'name': 'Beverages & Treats', 'slug': 'beverages-treats'},
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
                'name': 'Fresh Juice',
                'description': 'Freshly squeezed orange juice',
                'price': 5.99,
                'category': 'beverages-treats',
                'image': 'https://images.unsplash.com/photo-1622597480248-ec889cbde4b5?w=400'
            },
            {
                'name': 'Chocolate Cake',
                'description': 'Rich chocolate cake with cream filling',
                'price': 8.99,
                'category': 'beverages-treats',
                'image': 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=400'
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
        
        # Create sample catering services
        catering_services_data = [
            {
                'name': 'Event Setup',
                'short_description': 'Professional event setup and decoration services for weddings, corporate events, and special occasions.',
                'detailed_description': '''Our comprehensive event setup service includes everything you need to create a memorable occasion. We handle all aspects of event preparation including:

• Venue decoration and theming
• Table and chair arrangement
• Lighting and sound setup
• Floral arrangements and centerpieces
• Custom signage and branding
• Professional staff coordination

Whether it's an intimate gathering or a large corporate event, our experienced team ensures every detail is perfect. We work closely with you to understand your vision and bring it to life with precision and style.

Our setup service is available for:
- Weddings and receptions
- Corporate events and meetings
- Birthday parties and celebrations
- Holiday gatherings
- Special occasions of all kinds''',
                'icon': 'fas fa-calendar-check',
                'features': [
                    'Professional decoration and theming',
                    'Complete venue setup and arrangement',
                    'Custom lighting and sound',
                    'Floral arrangements and centerpieces',
                    'Staff coordination and management',
                    'Cleanup and breakdown service'
                ],
                'pricing_info': 'Starting from $500 for basic setup. Custom quotes available for larger events.',
                'order': 1
            },
            {
                'name': 'Custom Menus',
                'short_description': 'Tailored menu planning to match your event theme and dietary requirements.',
                'detailed_description': '''Create the perfect dining experience with our custom menu planning service. We work with you to design menus that reflect your event's theme, accommodate dietary restrictions, and exceed your guests' expectations.

Our menu planning process includes:

• Initial consultation and theme discussion
• Dietary requirement assessment
• Menu proposal and tasting sessions
• Final menu customization
• Ingredient sourcing and preparation planning
• Staff training for special dietary needs

We specialize in:
- Vegetarian and vegan options
- Gluten-free and allergen-free menus
- Cultural and traditional cuisine
- Seasonal and local ingredients
- Dietary restriction accommodations
- Children's menu options

Our chefs are experienced in creating diverse menus that cater to all preferences while maintaining the highest quality standards.''',
                'icon': 'fas fa-utensils',
                'features': [
                    'Personalized menu consultation',
                    'Dietary restriction accommodation',
                    'Tasting sessions available',
                    'Cultural and theme-based menus',
                    'Seasonal ingredient focus',
                    'Children\'s menu options'
                ],
                'pricing_info': 'Menu planning consultation: $100. Custom pricing based on complexity and requirements.',
                'order': 2
            },
            {
                'name': 'Delivery & Setup',
                'short_description': 'Reliable delivery and professional setup at your venue with attention to every detail.',
                'detailed_description': '''Our delivery and setup service ensures your catering arrives on time and is presented beautifully at your venue. We handle all logistics so you can focus on enjoying your event.

Our delivery service includes:

• Timely delivery to your venue
• Professional food presentation
• Equipment and serving ware setup
• Temperature-controlled transportation
• On-site staff for setup and service
• Post-event cleanup and removal

We provide:
- Punctual delivery scheduling
- Professional presentation setup
- Serving equipment and utensils
- Temperature monitoring
- On-site coordination
- Cleanup and breakdown

Our experienced delivery team ensures everything arrives in perfect condition and is set up according to your specifications. We coordinate with your venue staff to ensure seamless service.''',
                'icon': 'fas fa-truck',
                'features': [
                    'Punctual delivery scheduling',
                    'Professional food presentation',
                    'Equipment and serving ware',
                    'Temperature-controlled transport',
                    'On-site setup coordination',
                    'Post-event cleanup service'
                ],
                'pricing_info': 'Delivery fee: $50-150 depending on distance. Setup service: $25-75 per hour.',
                'order': 3
            }
        ]
        
        for service_data in catering_services_data:
            service, created = CateringService.objects.get_or_create(
                name=service_data['name'],
                defaults={
                    'short_description': service_data['short_description'],
                    'detailed_description': service_data['detailed_description'],
                    'icon': service_data['icon'],
                    'features': service_data['features'],
                    'pricing_info': service_data['pricing_info'],
                    'order': service_data['order'],
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'✅ Created catering service: {service.name}')
        
        self.stdout.write(self.style.SUCCESS('✅ Sample data added successfully!'))
