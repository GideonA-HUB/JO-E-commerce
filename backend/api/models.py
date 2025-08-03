from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Avg, Count
import stripe

from django.contrib.auth import get_user_model
User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return self.name

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('finger-foods', 'Finger Foods'),
        ('beverages', 'Beverages'),
        ('desserts', 'Desserts'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    image = models.URLField(blank=True, null=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    @property
    def average_rating(self):
        """Calculate average rating for the product"""
        avg = self.reviews.aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else 0
    
    @property
    def review_count(self):
        """Get total number of reviews"""
        return self.reviews.count()
    
    @property
    def rating_distribution(self):
        """Get rating distribution (1-5 stars)"""
        distribution = {}
        for i in range(1, 6):
            count = self.reviews.filter(rating=i).count()
            distribution[i] = count
        return distribution
    
    def get_related_products(self, limit=4):
        """Get related products based on category"""
        return Product.objects.filter(
            category=self.category,
            is_available=True
        ).exclude(id=self.id)[:limit]
    
    def get_recommendations(self, limit=4):
        """Get product recommendations based on similar ratings"""
        # Get products with similar average ratings
        similar_products = Product.objects.filter(
            is_available=True,
            reviews__rating__gte=self.average_rating - 1,
            reviews__rating__lte=self.average_rating + 1
        ).exclude(id=self.id).distinct()
        
        # If not enough similar products, get products from same category
        if similar_products.count() < limit:
            category_products = self.get_related_products(limit - similar_products.count())
            return list(similar_products) + list(category_products)
        
        return similar_products[:limit]

class ProductReview(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    is_verified_purchase = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['product', 'customer_email']  # One review per customer per product
    
    def __str__(self):
        return f"{self.customer_name} - {self.product.name} ({self.rating} stars)"
    
    def save(self, *args, **kwargs):
        # Check if customer has purchased this product
        from .models import Order, OrderItem
        has_purchased = OrderItem.objects.filter(
            order__email=self.customer_email,
            product=self.product,
            order__status__in=['confirmed', 'preparing', 'ready', 'delivered']
        ).exists()
        self.is_verified_purchase = has_purchased
        super().save(*args, **kwargs)

class Wishlist(models.Model):
    customer_email = models.EmailField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['customer_email', 'product']
        ordering = ['-added_at']
    
    def __str__(self):
        return f"{self.customer_email} - {self.product.name}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready for Pickup'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Customer Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    
    # Delivery Information
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    delivery_instructions = models.TextField(blank=True, null=True)
    
    # Order Information
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def customer_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def delivery_address(self):
        return f"{self.address}, {self.city}, {self.state} {self.zip_code}"
    
    def __str__(self):
        return f"Order #{self.id} - {self.customer_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

class SiteSettings(models.Model):
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    hours = models.CharField(max_length=100, blank=True)
    facebook = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    tiktok = models.URLField(blank=True)
    youtube = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Site Settings'
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and SiteSettings.objects.exists():
            return
        super().save(*args, **kwargs)
    
    def __str__(self):
        return "Site Settings"
    
    @classmethod
    def get_settings(cls):
        """Get the current site settings, creating default if none exist"""
        settings_obj, created = cls.objects.get_or_create(
            pk=1,
            defaults={
                'phone': '+1 (555) 123-4567',
                'email': 'info@tastyfingers.com',
                'address': '123 Food Street, Culinary District',
                'hours': 'Mon-Sat: 9AM-9PM',
            }
        )
        return settings_obj

class CateringService(models.Model):
    name = models.CharField(max_length=200)
    short_description = models.TextField()
    detailed_description = models.TextField()
    icon = models.CharField(max_length=50, help_text="FontAwesome icon class (e.g., 'fas fa-calendar-check')")
    features = models.JSONField(default=list, help_text="List of features as JSON array")
    pricing_info = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name

class ContactMessage(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('read', 'Read'),
        ('replied', 'Replied'),
        ('archived', 'Archived'),
    ]
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Message from {self.first_name} {self.last_name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

# Signal removed - Telegram notifications disabled

class ProductRating(models.Model):
    product = models.ForeignKey(Product, related_name='ratings', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    user_email = models.EmailField(blank=True, null=True)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['product', 'user_email']
        ordering = ['-created_at']

    def __str__(self):
        user_identifier = self.user.username if self.user else self.user_email
        return f"{user_identifier} - {self.product.name} ({self.rating} stars)"

class ProductComment(models.Model):
    product = models.ForeignKey(Product, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    user_email = models.EmailField(blank=True, null=True)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['product', 'user_email']
        ordering = ['-created_at']

    def __str__(self):
        user_identifier = self.user.username if self.user else self.user_email
        return f"{user_identifier} - {self.product.name}"

class BlogPost(models.Model):
    CATEGORY_CHOICES = [
        ('recipes', 'Recipes'),
        ('tips', 'Food Tips'),
        ('updates', 'Company Updates'),
    ]
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    image = models.URLField(blank=True, null=True)
    author = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='updates')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-subscribed_at']

    def __str__(self):
        return self.email

class NewsletterCampaign(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
    ]
    
    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=200)
    content = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    recipients = models.ManyToManyField(NewsletterSubscriber, through='CampaignRecipient')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class CampaignRecipient(models.Model):
    campaign = models.ForeignKey(NewsletterCampaign, on_delete=models.CASCADE)
    subscriber = models.ForeignKey(NewsletterSubscriber, on_delete=models.CASCADE)
    sent_at = models.DateTimeField(auto_now_add=True)
    opened = models.BooleanField(default=False)
    clicked = models.BooleanField(default=False)

    class Meta:
        unique_together = ['campaign', 'subscriber']
