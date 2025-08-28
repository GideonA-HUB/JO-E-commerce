from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from django.db.models import Sum, Q
from django.core.validators import MinValueValidator, MaxValueValidator
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import serializers
import json
from decimal import Decimal

# Import Paystack service
from .paystack_service import PaystackService
from .models import (
    Product, Order, OrderItem, CateringService, ProductReview, 
    Wishlist, ProductRating, ProductComment, BlogPost,
    NewsletterSubscriber, NewsletterCampaign, CampaignRecipient,
    SiteSettings, ContactMessage
)
from .serializers import (
    ProductSerializer, OrderSerializer, CreateOrderSerializer,
    CateringServiceSerializer, ProductReviewSerializer, CreateProductReviewSerializer,
    WishlistSerializer, CreateWishlistSerializer,
    ProductRatingSerializer, CreateProductRatingSerializer,
    ProductCommentSerializer, CreateProductCommentSerializer,
    BlogPostSerializer, NewsletterSubscriberSerializer,
    NewsletterCampaignSerializer, CampaignRecipientSerializer,
    SiteSettingsSerializer, ContactMessageSerializer
)
from accounts.models import UserProfile

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
            
            # Check if Paystack is properly configured
            paystack_configured = (
                settings.PAYSTACK_PUBLIC_KEY != 'pk_test_your_paystack_public_key_here' and
                settings.PAYSTACK_SECRET_KEY != 'sk_test_your_paystack_secret_key_here'
            )
            
            if paystack_configured:
                # Initialize Paystack transaction
                try:
                    paystack_service = PaystackService()
                    
                    # Prepare order data for Paystack
                    order_data = {
                        'email': order.email,
                        'total_amount': float(order.total_amount),
                        'order_id': order.id,
                        'first_name': order.first_name,
                        'last_name': order.last_name,
                        'phone': order.phone,
                        'address': order.address,
                        'items': [
                            {
                                'product_id': item.product.id,
                                'product_name': item.product.name,
                                'quantity': item.quantity,
                                'price': float(item.product.price)
                            }
                            for item in order.items.all()
                        ]
                    }
                    
                    # Initialize transaction
                    result = paystack_service.initialize_transaction(order_data)
                    
                    if result['success']:
                        # Store Paystack reference in order
                        order.paystack_reference = result['reference']
                        order.save()
                        
                        return Response({
                            'order': OrderSerializer(order).data,
                            'authorization_url': result['authorization_url'],
                            'reference': result['reference'],
                            'access_code': result['access_code'],
                            'public_key': settings.PAYSTACK_PUBLIC_KEY
                        }, status=status.HTTP_201_CREATED)
                    else:
                        order.delete()  # Delete order if transaction initialization fails
                        return Response({
                            'error': result['error']
                        }, status=status.HTTP_400_BAD_REQUEST)
                        
                except Exception as e:
                    order.delete()  # Delete order if any error occurs
                    return Response({
                        'error': f'Payment initialization failed: {str(e)}'
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Test mode - create order without Paystack
                order.status = 'pending'
                order.save()
                
                return Response({
                    'order': OrderSerializer(order).data,
                    'reference': f"TEST_REF_{order.id}",
                    'access_code': f"TEST_ACCESS_{order.id}",
                    'public_key': 'pk_test_placeholder',
                    'test_mode': True,
                    'message': 'Order created in test mode. Paystack not configured.'
                }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def confirm_payment(self, request, pk=None):
        order = self.get_object()
        reference = request.data.get('reference')
        
        # Check if Paystack is properly configured
        paystack_configured = (
            settings.PAYSTACK_PUBLIC_KEY != 'pk_test_your_paystack_public_key_here' and
            settings.PAYSTACK_SECRET_KEY != 'sk_test_your_paystack_secret_key_here'
        )
        
        if paystack_configured:
            if reference:
                try:
                    paystack_service = PaystackService()
                    result = paystack_service.verify_transaction(reference)
                    
                    if result['success'] and result['status'] == 'success':
                        order.status = 'confirmed'
                        order.payment_reference = reference
                        order.payment_amount = result['amount']
                        order.payment_date = timezone.now()
                        order.save()
                        
                        # Send confirmation email
                        try:
                            send_mail(
                                subject=f'Order Confirmed - {settings.SITE_NAME}',
                                message=f'''
                                Thank you for your order!
                                
                                Order #: {order.id}
                                Total: ₦{order.total_amount}
                                Payment Reference: {reference}
                                
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
                            'message': 'Payment confirmed and order placed successfully!',
                            'reference': reference,
                            'amount': result['amount']
                        })
                    else:
                        return Response({
                            'error': result.get('error', 'Payment verification failed')
                        }, status=status.HTTP_400_BAD_REQUEST)
                        
                except Exception as e:
                    return Response({
                        'error': f'Payment verification failed: {str(e)}'
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    'error': 'Payment reference is required'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Test mode - simulate payment confirmation
            order.status = 'confirmed'
            order.payment_reference = f"TEST_REF_{order.id}"
            order.payment_amount = order.total_amount
            order.payment_date = timezone.now()
            order.save()
            
            return Response({
                'success': True,
                'message': 'Payment confirmed in test mode!',
                'reference': f"TEST_REF_{order.id}",
                'amount': float(order.total_amount),
                'test_mode': True
            })

class ProductReviewViewSet(viewsets.ModelViewSet):
    queryset = ProductReview.objects.all()
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CreateProductReviewSerializer
        return ProductReviewSerializer
    
    def create(self, request, *args, **kwargs):
        try:
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
            
        except Exception as e:
            # Check if it's a duplicate review error
            customer_email = request.data.get('customer_email')
            product_id = request.data.get('product')
            
            if customer_email and product_id:
                existing_review = ProductReview.objects.filter(
                    product_id=product_id,
                    customer_email=customer_email
                ).first()
                
                if existing_review:
                    return Response({
                        'error': 'You have already submitted a review for this product. You can only submit one review per product.'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # For other errors, return a generic message
            return Response({
                'error': 'Error submitting review. Please try again.'
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

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            # Check if it's a duplicate rating error
            user_email = request.data.get('user_email') or (request.user.email if request.user.is_authenticated else None)
            product_id = request.data.get('product')
            
            if user_email and product_id:
                # Check if user has already rated this product
                existing_rating = ProductRating.objects.filter(
                    product_id=product_id,
                    user_email=user_email
                ).first()
                
                if existing_rating:
                    return Response({
                        'error': 'You have already submitted a rating for this product. You can only submit one rating per product.'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # For other errors, return a generic message
            return Response({
                'error': 'Error submitting rating. Please try again.'
            }, status=status.HTTP_400_BAD_REQUEST)

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

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            # Check if it's a duplicate comment error
            user_email = request.data.get('user_email') or (request.user.email if request.user.is_authenticated else None)
            product_id = request.data.get('product')
            
            if user_email and product_id:
                # Check if user has already commented on this product
                existing_comment = ProductComment.objects.filter(
                    product_id=product_id,
                    user_email=user_email
                ).first()
                
                if existing_comment:
                    return Response({
                        'error': 'You have already submitted a review for this product. You can only submit one review per product.'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # For other errors, return a generic message
            return Response({
                'error': 'Error submitting review. Please try again.'
            }, status=status.HTTP_400_BAD_REQUEST)

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
        
        if not subscribers.exists():
            return Response({
                'error': 'No active subscribers found.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create campaign recipients and send emails
        sent_count = 0
        failed_count = 0
        
        for subscriber in subscribers:
            try:
                # Create campaign recipient record
                recipient = CampaignRecipient.objects.create(
                    campaign=campaign,
                    subscriber=subscriber
                )
                
                # Prepare email context
                context = {
                    'campaign': campaign,
                    'subscriber': subscriber,
                    'unsubscribe_url': f"{settings.SITE_URL}/api/newsletter-subscribers/unsubscribe/",
                    'site_name': settings.SITE_NAME,
                    'site_url': settings.SITE_URL
                }
                
                # Render email template
                html_message = render_to_string('email/newsletter_campaign.html', context)
                plain_message = render_to_string('email/newsletter_campaign.txt', context)
                
                # Send email
                send_mail(
                    subject=campaign.subject,
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[subscriber.email],
                    html_message=html_message,
                    fail_silently=False
                )
                
                # Mark as sent
                recipient.sent_at = timezone.now()
                recipient.save()
                sent_count += 1
                
            except Exception as e:
                print(f"Failed to send email to {subscriber.email}: {e}")
                failed_count += 1
        
        # Update campaign status
        campaign.status = 'sent'
        campaign.sent_at = timezone.now()
        campaign.save()
        
        return Response({
            'message': f'Campaign sent successfully! {sent_count} emails sent, {failed_count} failed.',
            'sent_count': sent_count,
            'failed_count': failed_count
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
def paystack_webhook(request):
    """Handle Paystack webhook events"""
    try:
        # Verify webhook signature
        signature = request.headers.get('X-Paystack-Signature')
        if not signature:
            return Response({'error': 'No signature'}, status=400)
        
        # Verify webhook secret
        webhook_secret = settings.PAYSTACK_WEBHOOK_SECRET
        if webhook_secret == 'whsec_your_paystack_webhook_secret_here':
            # Test mode - accept all webhooks
            pass
        else:
            # In production, verify the signature
            import hmac
            import hashlib
            
            expected_signature = hmac.new(
                webhook_secret.encode('utf-8'),
                request.body,
                hashlib.sha512
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_signature):
                return Response({'error': 'Invalid signature'}, status=400)
        
        # Parse webhook data
        webhook_data = json.loads(request.body)
        event = webhook_data.get('event')
        data = webhook_data.get('data', {})
        
        if event == 'charge.success':
            # Payment successful
            reference = data.get('reference')
            amount = data.get('amount', 0) / 100  # Convert from kobo to naira
            
            try:
                order = Order.objects.get(paystack_reference=reference)
                order.status = 'confirmed'
                order.payment_reference = reference
                order.payment_amount = amount
                order.payment_date = timezone.now()
                order.save()
                
                # Send confirmation email
                try:
                    send_mail(
                        subject=f'Payment Confirmed - {settings.SITE_NAME}',
                        message=f'''
                        Payment received for your order!
                        
                        Order #: {order.id}
                        Amount: ₦{amount}
                        Reference: {reference}
                        
                        Your order is being processed.
                        
                        Best regards,
                        {settings.SITE_NAME} Team
                        ''',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[order.email],
                        fail_silently=True
                    )
                except Exception as e:
                    print(f"Failed to send webhook email: {e}")
                
                return Response({'status': 'success'})
                
            except Order.DoesNotExist:
                return Response({'error': 'Order not found'}, status=404)
        
        elif event == 'charge.failed':
            # Payment failed
            reference = data.get('reference')
            try:
                order = Order.objects.get(paystack_reference=reference)
                order.status = 'failed'
                order.save()
                
                # Send failure notification
                try:
                    send_mail(
                        subject=f'Payment Failed - {settings.SITE_NAME}',
                        message=f'''
                        Payment failed for your order.
                        
                        Order #: {order.id}
                        Reference: {reference}
                        
                        Please try again or contact support.
                        
                        Best regards,
                        {settings.SITE_NAME} Team
                        ''',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[order.email],
                        fail_silently=True
                    )
                except Exception as e:
                    print(f"Failed to send failure email: {e}")
                
                return Response({'status': 'success'})
                
            except Order.DoesNotExist:
                return Response({'error': 'Order not found'}, status=404)
        
        return Response({'status': 'success'})
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def customer_orders(request):
    """Get orders for a specific customer by email"""
    email = request.query_params.get('email')
    if not email:
        return Response({'error': 'Email parameter is required'}, status=400)
    
    try:
        orders = Order.objects.filter(email=email).order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def order_tracking(request, order_id):
    """Get detailed order information for tracking"""
    try:
        order = Order.objects.get(id=order_id)
        serializer = OrderSerializer(order)
        return Response(serializer.data)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)



