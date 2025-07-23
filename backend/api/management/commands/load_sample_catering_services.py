from django.core.management.base import BaseCommand
from api.models import CateringService

class Command(BaseCommand):
    help = 'Load sample catering services data'

    def handle(self, *args, **options):
        # Clear existing services
        CateringService.objects.all().delete()
        
        services = [
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
        
        for service_data in services:
            CateringService.objects.create(**service_data)
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created catering service: {service_data["name"]}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully loaded {len(services)} catering services')
        ) 