from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'products', views.ProductViewSet)
router.register(r'orders', views.OrderViewSet)
router.register(r'catering-services', views.CateringServiceViewSet)
router.register(r'reviews', views.ProductReviewViewSet)
router.register(r'wishlist', views.WishlistViewSet)
router.register(r'product-ratings', views.ProductRatingViewSet)
router.register(r'product-comments', views.ProductCommentViewSet)
router.register(r'blog', views.BlogPostViewSet)
router.register(r'newsletter-subscribers', views.NewsletterSubscriberViewSet)
router.register(r'newsletter-campaigns', views.NewsletterCampaignViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('settings/', views.site_settings, name='site-settings'),
    path('contact/', views.contact, name='contact'),
    path('paystack-webhook/', views.paystack_webhook, name='paystack-webhook'),
    path('customer-orders/', views.customer_orders, name='customer-orders'),
    path('order-tracking/<int:order_id>/', views.order_tracking, name='order-tracking'),
] 