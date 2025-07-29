from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Order, OrderItem, SiteSettings, CateringService, ContactMessage, ProductReview, Wishlist, ProductRating, ProductComment, BlogPost

# Customize admin site
admin.site.site_header = "CHOPHOUSE Admin"
admin.site.site_title = "CHOPHOUSE Admin Portal"
admin.site.index_title = "Welcome to CHOPHOUSE Administration"

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('phone', 'email', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('phone', 'email', 'address', 'hours')
        }),
        ('Social Media', {
            'fields': ('facebook', 'instagram', 'twitter', 'tiktok', 'youtube'),
            'description': 'Add your social media profile URLs'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # Only allow one site settings instance
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion of site settings
        return False

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_available', 'created_at', 'image_preview')
    list_filter = ('category', 'is_available', 'created_at')
    search_fields = ('name', 'description')
    list_editable = ('price', 'is_available')
    ordering = ('-created_at',)
    actions = ['make_available', 'make_unavailable']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px;" />', obj.image)
        return "No Image"
    image_preview.short_description = 'Image'
    
    def make_available(self, request, queryset):
        updated = queryset.update(is_available=True)
        self.message_user(request, f'{updated} products marked as available.')
    make_available.short_description = "Mark selected products as available"
    
    def make_unavailable(self, request, queryset):
        updated = queryset.update(is_available=False)
        self.message_user(request, f'{updated} products marked as unavailable.')
    make_unavailable.short_description = "Mark selected products as unavailable"
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'category')
        }),
        ('Pricing & Availability', {
            'fields': ('price', 'is_available')
        }),
        ('Media', {
            'fields': ('image',)
        }),
    )

@admin.register(CateringService)
class CateringServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'short_description']
    list_editable = ['order', 'is_active']
    ordering = ['order', 'name']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'short_description', 'detailed_description', 'icon')
        }),
        ('Features & Pricing', {
            'fields': ('features', 'pricing_info')
        }),
        ('Settings', {
            'fields': ('is_active', 'order')
        }),
    )

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'status', 'created_at', 'ip_address']
    list_filter = ['status', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'message']
    readonly_fields = ['created_at', 'updated_at', 'ip_address']
    list_editable = ['status']
    ordering = ['-created_at']
    fieldsets = (
        ('Contact Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Message', {
            'fields': ('message',)
        }),
        ('Status & Tracking', {
            'fields': ('status', 'ip_address', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'Full Name'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'total_amount', 'status', 'created_at', 'item_count')
    list_filter = ('status', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    readonly_fields = ('created_at', 'updated_at', 'stripe_payment_intent_id')
    actions = ['mark_confirmed', 'mark_preparing', 'mark_ready', 'mark_delivered', 'mark_cancelled']
    
    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Items'
    
    def mark_confirmed(self, request, queryset):
        updated = queryset.update(status='confirmed')
        self.message_user(request, f'{updated} orders marked as confirmed.')
    mark_confirmed.short_description = "Mark selected orders as confirmed"
    
    def mark_preparing(self, request, queryset):
        updated = queryset.update(status='preparing')
        self.message_user(request, f'{updated} orders marked as preparing.')
    mark_preparing.short_description = "Mark selected orders as preparing"
    
    def mark_ready(self, request, queryset):
        updated = queryset.update(status='ready')
        self.message_user(request, f'{updated} orders marked as ready for pickup.')
    mark_ready.short_description = "Mark selected orders as ready for pickup"
    
    def mark_delivered(self, request, queryset):
        updated = queryset.update(status='delivered')
        self.message_user(request, f'{updated} orders marked as delivered.')
    mark_delivered.short_description = "Mark selected orders as delivered"
    
    def mark_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} orders marked as cancelled.')
    mark_cancelled.short_description = "Mark selected orders as cancelled"
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Delivery Information', {
            'fields': ('address', 'city', 'state', 'zip_code', 'delivery_instructions')
        }),
        ('Order Details', {
            'fields': ('total_amount', 'status', 'stripe_payment_intent_id')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price']
    list_filter = ['order__status']
    search_fields = ['order__customer_name', 'product__name']

@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'customer_name', 'rating', 'is_verified_purchase', 'created_at']
    list_filter = ['rating', 'is_verified_purchase', 'created_at', 'product__category']
    search_fields = ['customer_name', 'customer_email', 'comment', 'product__name']
    readonly_fields = ['created_at', 'updated_at', 'is_verified_purchase']
    list_editable = ['rating']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Review Information', {
            'fields': ('product', 'customer_name', 'customer_email', 'rating', 'comment')
        }),
        ('Status', {
            'fields': ('is_verified_purchase', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product')

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['customer_email', 'product', 'added_at']
    list_filter = ['added_at', 'product__category']
    search_fields = ['customer_email', 'product__name']
    readonly_fields = ['added_at']
    ordering = ['-added_at']
    
    fieldsets = (
        ('Wishlist Item', {
            'fields': ('customer_email', 'product')
        }),
        ('Timestamps', {
            'fields': ('added_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product')

@admin.register(ProductRating)
class ProductRatingAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'created_at']
    list_filter = ['product', 'user', 'rating', 'created_at']
    search_fields = ['product__name', 'user__username']

@admin.register(ProductComment)
class ProductCommentAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'comment', 'created_at']
    list_filter = ['product', 'user', 'created_at']
    search_fields = ['product__name', 'user__username', 'comment']

admin.site.register(BlogPost)
