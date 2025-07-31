from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import stripe
import json
from .models import Product, Order, OrderItem, SiteSettings, CateringService, ContactMessage, ProductReview, Wishlist, ProductRating, ProductComment, BlogPost, NewsletterSubscriber, NewsletterCampaign, CampaignRecipient
from .serializers import (
    ProductSerializer, OrderSerializer, CreateOrderSerializer,
    SiteSettingsSerializer, CateringServiceSerializer, ContactMessageSerializer,
    ProductReviewSerializer, CreateProductReviewSerializer, WishlistSerializer, CreateWishlistSerializer,
    ProductRatingSerializer, CreateProductRatingSerializer, ProductCommentSerializer, CreateProductCommentSerializer,
    BlogPostSerializer, NewsletterSubscriberSerializer, NewsletterCampaignSerializer
)
from django.utils import timezone
from rest_framework import serializers

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()  # Removed is_available=True filter
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'price']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price', 'created_at', 'average_rating']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Add customer email to context for wishlist checking
        customer_email = self.request.query_params.get('customer_email')
        if customer_email:
            self.request.customer_email = customer_email
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        category = request.query_params.get('category')
        if category:
            products = self.queryset.filter(category=category)
            serializer = self.get_serializer(products, many=True)
            return Response(serializer.data)
        return Response({'error': 'Category parameter required'}, status=400)
    
    @action(detail=True, methods=['get'])
    def recommendations(self, request, pk=None):
        product = self.get_object()
        recommendations = product.get_recommendations()
        serializer = self.get_serializer(recommendations, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('q', '')
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        category = request.query_params.get('category')
        rating = request.query_params.get('rating')
        
        queryset = self.queryset
        
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )
        
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        if category:
            queryset = queryset.filter(category=category)
        
        if rating:
            queryset = queryset.filter(reviews__rating__gte=rating).distinct()
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class CateringServiceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CateringService.objects.all()  # Removed is_active=True filter
    serializer_class = CateringServiceSerializer
    permission_classes = [AllowAny]
    pagination_class = None

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CreateOrderSerializer
        return OrderSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            order = serializer.save()
            
            # Create Stripe Payment Intent
            try:
                payment_intent = stripe.PaymentIntent.create(
                    amount=int(order.total_amount * 100),  # Convert to cents
                    currency='ngn',  # Nigerian Naira
                    metadata={
                        'order_id': order.id,
                        'customer_email': order.email
                    }
                )
                
                order.stripe_payment_intent_id = payment_intent.id
                order.save()
                
                return Response({
                    'order': OrderSerializer(order).data,
                    'client_secret': payment_intent.client_secret,
                    'publishable_key': settings.STRIPE_PUBLISHABLE_KEY
                }, status=status.HTTP_201_CREATED)
                
            except stripe.error.StripeError as e:
                order.delete()  # Delete order if payment intent creation fails
                return Response({
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def confirm_payment(self, request, pk=None):
        order = self.get_object()
        payment_intent_id = request.data.get('payment_intent_id')
        
        if payment_intent_id and payment_intent_id == order.stripe_payment_intent_id:
            try:
                payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
                if payment_intent.status == 'succeeded':
                    order.status = 'confirmed'
                    order.save()
                    
                    # Send confirmation email
                    try:
                        send_mail(
                            subject=f'Order Confirmed - {settings.SITE_NAME}',
                            message=f'''
                            Thank you for your order!
                            
                            Order #: {order.id}
                            Total: ₦{order.total_amount}
                            
                            We'll start preparing your order right away.
                            You'll receive updates on your order status.
                            
                            Best regards,
                            {settings.SITE_NAME} Team
                            ''',
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[order.email],
                            fail_silently=True
                        )
                    except Exception as e:
                        print(f"Failed to send confirmation email: {e}")
                    
                    return Response({
                        'success': True,
                        'message': 'Payment confirmed and order placed successfully!'
                    })
                else:
                    return Response({
                        'error': 'Payment not completed'
                    }, status=status.HTTP_400_BAD_REQUEST)
            except stripe.error.StripeError as e:
                return Response({
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'error': 'Invalid payment intent'
        }, status=status.HTTP_400_BAD_REQUEST)

class ProductReviewViewSet(viewsets.ModelViewSet):
    queryset = ProductReview.objects.all()
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CreateProductReviewSerializer
        return ProductReviewSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            review = serializer.save()
            
            # Send notification email to admin
            try:
                send_mail(
                    subject=f'New Product Review - {review.product.name}',
                    message=f'''
                    New review received:
                    
                    Product: {review.product.name}
                    Customer: {review.customer_name}
                    Rating: {review.rating}/5
                    Comment: {review.comment}
                    Verified Purchase: {review.is_verified_purchase}
                    ''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.ADMIN_EMAIL],
                    fail_silently=True
                )
            except Exception as e:
                print(f"Failed to send review notification: {e}")
            
            return Response({
                'success': True,
                'message': 'Review submitted successfully!'
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def by_product(self, request):
        product_id = request.query_params.get('product_id')
        if product_id:
            reviews = self.queryset.filter(product_id=product_id)
            serializer = self.get_serializer(reviews, many=True)
            return Response(serializer.data)
        return Response({'error': 'Product ID required'}, status=400)

class WishlistViewSet(viewsets.ModelViewSet):
    queryset = Wishlist.objects.all()
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CreateWishlistSerializer
        return WishlistSerializer
    
    def list(self, request, *args, **kwargs):
        customer_email = request.query_params.get('customer_email')
        if customer_email:
            wishlist_items = self.queryset.filter(customer_email=customer_email)
            serializer = self.get_serializer(wishlist_items, many=True)
            return Response(serializer.data)
        return Response({'error': 'Customer email required'}, status=400)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            wishlist_item = serializer.save()
            return Response({
                'success': True,
                'message': 'Item added to wishlist!'
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        customer_email = request.data.get('user_email')
        product_id = request.data.get('product')
        
        if customer_email and product_id:
            try:
                # Check if item already exists
                existing_item = self.queryset.filter(
                    customer_email=customer_email,
                    product_id=product_id
                ).first()
                
                if existing_item:
                    return Response({
                        'success': True,
                        'message': 'Item already in wishlist!'
                    })
                
                # Create new wishlist item
                wishlist_item = self.queryset.create(
                    customer_email=customer_email,
                    product_id=product_id
                )
                
                return Response({
                    'success': True,
                    'message': 'Item added to wishlist!'
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response({
                    'error': f'Failed to add item to wishlist: {str(e)}'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'error': 'Customer email and product ID required'
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        user_email = request.data.get('user_email')
        product_id = request.data.get('product')
        
        if user_email and product_id:
            try:
                wishlist_item = self.queryset.get(
                    customer_email=user_email,
                    product_id=product_id
                )
                wishlist_item.delete()
                return Response({
                    'success': True,
                    'message': 'Item removed from wishlist!'
                })
            except Wishlist.DoesNotExist:
                return Response({
                    'error': 'Item not found in wishlist'
                }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'error': 'User email and product ID required'
        }, status=status.HTTP_400_BAD_REQUEST)

class ProductRatingViewSet(viewsets.ModelViewSet):
    queryset = ProductRating.objects.all()
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateProductRatingSerializer
        return ProductRatingSerializer

    def perform_create(self, serializer):
        # Handle case where user is not authenticated
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user, user_email=self.request.user.email)
        else:
            # For unauthenticated users, use user_email from request data
            user_email = self.request.data.get('user_email')
            if user_email:
                serializer.save(user=None, user_email=user_email)
            else:
                raise serializers.ValidationError("user_email is required for unauthenticated users")

    def get_queryset(self):
        queryset = super().get_queryset()
        product_id = self.request.query_params.get('product_id')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset

class ProductCommentViewSet(viewsets.ModelViewSet):
    queryset = ProductComment.objects.all()
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateProductCommentSerializer
        return ProductCommentSerializer

    def perform_create(self, serializer):
        # Handle case where user is not authenticated
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user, user_email=self.request.user.email)
        else:
            # For unauthenticated users, use user_email from request data
            user_email = self.request.data.get('user_email')
            if user_email:
                serializer.save(user=None, user_email=user_email)
            else:
                raise serializers.ValidationError("user_email is required for unauthenticated users")

    def get_queryset(self):
        queryset = super().get_queryset()
        product_id = self.request.query_params.get('product_id')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset

class BlogPostViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    lookup_field = 'slug'

class NewsletterSubscriberViewSet(viewsets.ModelViewSet):
    queryset = NewsletterSubscriber.objects.all()
    serializer_class = NewsletterSubscriberSerializer
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def subscribe(self, request):
        email = request.data.get('email')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        
        if not email:
            return Response({
                'error': 'Email is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            subscriber, created = NewsletterSubscriber.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'is_active': True
                }
            )
            
            if not created and subscriber.is_active:
                return Response({
                    'message': 'You are already subscribed to our newsletter!'
                }, status=status.HTTP_200_OK)
            
            if not created and not subscriber.is_active:
                subscriber.is_active = True
                subscriber.unsubscribed_at = None
                subscriber.save()
                return Response({
                    'message': 'Welcome back! You have been resubscribed to our newsletter.'
                }, status=status.HTTP_200_OK)
            
            return Response({
                'message': 'Thank you for subscribing to our newsletter!'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': 'Failed to subscribe. Please try again.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def unsubscribe(self, request):
        email = request.data.get('email')
        
        if not email:
            return Response({
                'error': 'Email is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            subscriber = NewsletterSubscriber.objects.get(email=email)
            subscriber.is_active = False
            subscriber.unsubscribed_at = timezone.now()
            subscriber.save()
            
            return Response({
                'message': 'You have been unsubscribed from our newsletter.'
            }, status=status.HTTP_200_OK)
            
        except NewsletterSubscriber.DoesNotExist:
            return Response({
                'error': 'Email not found in our subscribers list.'
            }, status=status.HTTP_404_NOT_FOUND)

class NewsletterCampaignViewSet(viewsets.ModelViewSet):
    queryset = NewsletterCampaign.objects.all()
    serializer_class = NewsletterCampaignSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def send_campaign(self, request, pk=None):
        campaign = self.get_object()
        
        if campaign.status == 'sent':
            return Response({
                'error': 'Campaign has already been sent.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get all active subscribers
        subscribers = NewsletterSubscriber.objects.filter(is_active=True)
        
        # Create campaign recipients
        for subscriber in subscribers:
            CampaignRecipient.objects.create(
                campaign=campaign,
                subscriber=subscriber
            )
        
        # Send emails (this would integrate with your email service)
        # For now, we'll just mark as sent
        campaign.status = 'sent'
        campaign.sent_at = timezone.now()
        campaign.save()
        
        return Response({
            'message': f'Campaign sent to {subscribers.count()} subscribers.'
        }, status=status.HTTP_200_OK)

@api_view(['GET'])
def site_settings(request):
    settings_obj = SiteSettings.get_settings()
    serializer = SiteSettingsSerializer(settings_obj)
    return Response(serializer.data)

@api_view(['GET'])
def catering_services(request):
    services = CateringService.objects.filter(is_active=True)
    serializer = CateringServiceSerializer(services, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def contact(request):
    serializer = ContactMessageSerializer(data=request.data)
    if serializer.is_valid():
        contact_message = serializer.save()
        
        # Send notification email to admin
        try:
            send_mail(
                subject=f'New Contact Message - {settings.SITE_NAME}',
                message=f'''
                New contact message received:
                
                From: {contact_message.full_name}
                Email: {contact_message.email}
                Phone: {contact_message.phone}
                
                Message:
                {contact_message.message}
                ''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL],
                fail_silently=True
            )
        except Exception as e:
            print(f"Failed to send admin notification: {e}")
        
        return Response({
            'success': True,
            'message': 'Thank you for your message! We\'ll get back to you soon.'
        })
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['POST'])
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)
    
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        order_id = payment_intent['metadata']['order_id']
        
        try:
            order = Order.objects.get(id=order_id)
            order.status = 'confirmed'
            order.save()
            
            # Send confirmation email
            try:
                send_mail(
                    subject=f'Order Confirmed - {settings.SITE_NAME}',
                    message=f'''
                    Thank you for your order!
                    
                    Order #: {order.id}
                    Total: ₦{order.total_amount}
                    
                    We'll start preparing your order right away.
                    You'll receive updates on your order status.
                    
                    Best regards,
                    {settings.SITE_NAME} Team
                    ''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[order.email],
                    fail_silently=True
                )
            except Exception as e:
                print(f"Failed to send confirmation email: {e}")
                
        except Order.DoesNotExist:
            pass
    
    return HttpResponse(status=200)



