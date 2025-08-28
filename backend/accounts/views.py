from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings
from .models import UserProfile
from api.models import ContactMessage, Order
from django.db.models import Q, Sum
from django.core.paginator import Paginator
from django.http import JsonResponse

def login_view(request):
    if request.user.is_authenticated:
        try:
            role = request.user.profile.role
        except Exception:
            logout(request)
            return redirect('login')
        if role in ['owner', 'staff']:
            return redirect('dashboard')
        else:
            return redirect('main_site')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
        except User.DoesNotExist:
            user = None
        
        if user is not None:
            # Check user role to determine session type
            try:
                role = user.profile.role
            except Exception:
                logout(request)
                messages.error(request, 'Profile error. Contact support.')
                return redirect('login')
            
            # Login the user
            login(request, user)
            
            # Create response based on role
            if role in ['owner', 'staff']:
                # This is an admin login - redirect to dashboard
                response = redirect('dashboard')
                # Set admin session cookie
                response.set_cookie(
                    getattr(settings, 'ADMIN_SESSION_COOKIE_NAME', 'admin_sessionid'),
                    request.session.session_key,
                    max_age=settings.SESSION_COOKIE_AGE,
                    domain=settings.SESSION_COOKIE_DOMAIN,
                    secure=settings.SESSION_COOKIE_SECURE,
                    httponly=settings.SESSION_COOKIE_HTTPONLY,
                    samesite=settings.SESSION_COOKIE_SAMESITE
                )
                return response
            else:
                # This is a customer login - redirect to main site
                response = redirect('main_site')
                # Set customer session cookie
                response.set_cookie(
                    getattr(settings, 'SESSION_COOKIE_NAME', 'customer_sessionid'),
                    request.session.session_key,
                    max_age=settings.SESSION_COOKIE_AGE,
                    domain=settings.SESSION_COOKIE_DOMAIN,
                    secure=settings.SESSION_COOKIE_SECURE,
                    httponly=settings.SESSION_COOKIE_HTTPONLY,
                    samesite=settings.SESSION_COOKIE_SAMESITE
                )
                return response
        else:
            messages.error(request, 'Invalid email or password.')
    
    return render(request, 'accounts/login.html')

def logout_view(request):
    # Determine which session to clear based on the user's role
    is_admin_user = False
    if request.user.is_authenticated:
        try:
            role = request.user.profile.role
            is_admin_user = role in ['owner', 'staff']
        except Exception:
            # If we can't determine role, default to customer
            is_admin_user = False
    
    # Logout the user
    logout(request)
    
    # Create response
    response = redirect(reverse('login'))
    
    # Clear the appropriate session cookie based on user role
    if is_admin_user:
        # Clear admin session cookie
        response.delete_cookie(getattr(settings, 'ADMIN_SESSION_COOKIE_NAME', 'admin_sessionid'))
    else:
        # Clear customer session cookie
        response.delete_cookie(getattr(settings, 'SESSION_COOKIE_NAME', 'customer_sessionid'))
    
    return response

@login_required(login_url='login')
def dashboard_view(request):
    try:
        profile = request.user.profile
    except Exception:
        logout(request)
        return redirect('login')
    context = {}
    if profile.role == 'owner':
        # Calculate real statistics
        context['total_contacts'] = ContactMessage.objects.count()
        context['unread_contacts'] = ContactMessage.objects.filter(status='new').count()
        context['total_orders'] = Order.objects.count()
        context['pending_orders'] = Order.objects.filter(status='pending').count()
        context['total_revenue'] = Order.objects.aggregate(total=Sum('total_amount'))['total'] or 0
        context['recent_contacts'] = ContactMessage.objects.order_by('-created_at')[:5]
        context['recent_orders'] = Order.objects.order_by('-created_at')[:5]
        context['is_owner'] = True
        staff_members = UserProfile.objects.filter(role__in=['staff', 'owner'])
        context['staff_count'] = staff_members.count()
        
        # Newsletter statistics
        from api.models import NewsletterSubscriber, NewsletterCampaign
        context['total_subscribers'] = NewsletterSubscriber.objects.count()
        context['active_subscribers'] = NewsletterSubscriber.objects.filter(is_active=True).count()
        context['total_campaigns'] = NewsletterCampaign.objects.count()
        context['sent_campaigns'] = NewsletterCampaign.objects.filter(status='sent').count()
        context['recent_subscribers'] = NewsletterSubscriber.objects.order_by('-subscribed_at')[:5]
        context['recent_campaigns'] = NewsletterCampaign.objects.order_by('-created_at')[:5]
        
    elif profile.role == 'staff':
        context['total_contacts'] = ContactMessage.objects.count()
        context['unread_contacts'] = ContactMessage.objects.filter(status='new').count()
        context['total_orders'] = Order.objects.count()
        context['pending_orders'] = Order.objects.filter(status='pending').count()
        context['total_revenue'] = Order.objects.aggregate(total=Sum('total_amount'))['total'] or 0
        context['recent_contacts'] = ContactMessage.objects.order_by('-created_at')[:5]
        context['recent_orders'] = Order.objects.order_by('-created_at')[:5]
        context['is_owner'] = False
        staff_members = UserProfile.objects.filter(role__in=['staff', 'owner'])
        context['staff_count'] = staff_members.count()
        
        # Newsletter statistics for staff
        from api.models import NewsletterSubscriber, NewsletterCampaign
        context['total_subscribers'] = NewsletterSubscriber.objects.count()
        context['active_subscribers'] = NewsletterSubscriber.objects.filter(is_active=True).count()
        context['total_campaigns'] = NewsletterCampaign.objects.count()
        context['sent_campaigns'] = NewsletterCampaign.objects.filter(status='sent').count()
        context['recent_subscribers'] = NewsletterSubscriber.objects.order_by('-subscribed_at')[:5]
        context['recent_campaigns'] = NewsletterCampaign.objects.order_by('-created_at')[:5]
        
    else:
        # If a customer tries to access dashboard, send them to main site
        return redirect('main_site')
    return render(request, 'accounts/dashboard.html', context)

@login_required(login_url='login')
def staff_management_view(request):
    profile = request.user.profile
    if profile.role != 'owner':
        return redirect('dashboard')
    
    # Get all staff and owner users (excluding regular customers)
    staff_members = UserProfile.objects.filter(role__in=['staff', 'owner'])
    
    if request.method == 'POST':
        # Check if it's an add action (form submission without action field)
        if 'email' in request.POST and 'password' in request.POST:
            email = request.POST.get('email')
            password = request.POST.get('password')
            role = request.POST.get('role', 'staff')
            
            if User.objects.filter(email=email).exists():
                messages.error(request, 'A user with that email already exists.')
            else:
                user = User.objects.create_user(username=email, email=email, password=password)
                user.profile.role = role
                user.profile.save()
                messages.success(request, f'{role.title()} user {email} added successfully.')
                return redirect('staff_management')
        
        # Check if it's a remove action
        elif 'action' in request.POST and request.POST.get('action') == 'remove':
            user_id = request.POST.get('user_id')
            try:
                user_to_remove = User.objects.get(id=user_id)
                if user_to_remove.profile.role in ['staff', 'owner'] and user_to_remove != request.user:
                    email = user_to_remove.email
                    user_to_remove.delete()
                    messages.success(request, f'User {email} removed successfully.')
                else:
                    messages.error(request, 'Cannot remove this user.')
            except User.DoesNotExist:
                messages.error(request, 'User not found.')
            return redirect('staff_management')
    
    # Calculate statistics
    total_staff = staff_members.count()
    owner_count = staff_members.filter(role='owner').count()
    staff_count = staff_members.filter(role='staff').count()
    
    context = {
        'staff_members': staff_members,
        'total_staff': total_staff,
        'owner_count': owner_count,
        'staff_count': staff_count,
    }
    
    return render(request, 'accounts/staff_management.html', context)

def register_view(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'A user with that email already exists.')
        else:
            user = User.objects.create_user(username=email, email=email, password=password)
            user.profile.role = 'user'
            user.profile.full_name = full_name
            user.profile.phone = phone
            user.profile.save()
            messages.success(request, 'Account created. Please log in.')
            return redirect('login')
    return render(request, 'accounts/register.html')

def staff_register_view(request):
    owner_exists = UserProfile.objects.filter(role='owner').exists()
    if request.method == 'POST':
        role = request.POST.get('role', 'staff' if owner_exists else 'owner')
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'A user with that email already exists.')
        elif role == 'owner' and owner_exists:
            messages.error(request, 'Owner already exists.')
        elif role not in ['owner', 'staff']:
            messages.error(request, 'Invalid role.')
        else:
            user = User.objects.create_user(username=email, email=email, password=password)
            user.profile.role = role
            user.profile.full_name = full_name
            user.profile.phone = phone
            user.profile.save()
            messages.success(request, f'{role.title()} account created. Please log in.')
            return redirect('staff_login')
    return render(request, 'accounts/staff_register.html', {'owner_exists': owner_exists})

def staff_login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = User.objects.get(email=email)
            if user.profile.role in ['owner', 'staff']:
                user = authenticate(request, username=user.username, password=password)
            else:
                user = None
        except User.DoesNotExist:
            user = None
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid email, password, or role.')
    return render(request, 'accounts/staff_login.html') 

@login_required(login_url='login')
def order_management(request):
    """Order management page for admin dashboard"""
    try:
        profile = request.user.profile
    except Exception:
        logout(request)
        return redirect('login')
    
    if profile.role not in ['owner', 'staff']:
        return redirect('dashboard')
    
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    
    # Get orders with filters
    orders = Order.objects.all().order_by('-created_at')
    
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    if search_query:
        orders = orders.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(id__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    confirmed_orders = Order.objects.filter(status='confirmed').count()
    preparing_orders = Order.objects.filter(status='preparing').count()
    ready_orders = Order.objects.filter(status='ready').count()
    delivered_orders = Order.objects.filter(status='delivered').count()
    cancelled_orders = Order.objects.filter(status='cancelled').count()
    
    context = {
        'page_obj': page_obj,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'confirmed_orders': confirmed_orders,
        'preparing_orders': preparing_orders,
        'ready_orders': ready_orders,
        'delivered_orders': delivered_orders,
        'cancelled_orders': cancelled_orders,
        'status_filter': status_filter,
        'search_query': search_query,
        'is_owner': profile.role == 'owner',
    }
    
    return render(request, 'accounts/order_management.html', context)

@login_required(login_url='login')
def update_order_status(request, order_id):
    """Update order status via AJAX"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
    try:
        profile = request.user.profile
    except Exception:
        return JsonResponse({'error': 'User not authenticated'}, status=401)
    
    if profile.role not in ['owner', 'staff']:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        order = Order.objects.get(id=order_id)
        new_status = request.POST.get('status')
        
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            
            # Send email notification to customer
            try:
                from django.core.mail import send_mail
                from django.conf import settings
                
                status_messages = {
                    'confirmed': 'Your order has been confirmed and is being prepared.',
                    'preparing': 'Your order is now being prepared in our kitchen.',
                    'ready': 'Your order is ready for pickup or delivery!',
                    'delivered': 'Your order has been delivered successfully.',
                    'cancelled': 'Your order has been cancelled.'
                }
                
                message = status_messages.get(new_status, f'Your order status has been updated to: {new_status}')
                
                send_mail(
                    subject=f'Order #{order.id} Status Update - {settings.SITE_NAME}',
                    message=f'''
                    Dear {order.first_name} {order.last_name},
                    
                    {message}
                    
                    Order Details:
                    - Order ID: #{order.id}
                    - Status: {new_status.title()}
                    - Total Amount: ₦{order.total_amount}
                    
                    Thank you for choosing {settings.SITE_NAME}!
                    
                    Best regards,
                    {settings.SITE_NAME} Team
                    ''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[order.email],
                    fail_silently=True
                )
            except Exception as e:
                print(f"Failed to send status update email: {e}")
            
            return JsonResponse({
                'success': True,
                'message': f'Order status updated to {new_status.title()}',
                'new_status': new_status
            })
        else:
            return JsonResponse({'error': 'Invalid status'}, status=400)
            
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required(login_url='login')
def subscriber_management(request):
    """Subscriber management page for admin dashboard"""
    try:
        profile = request.user.profile
    except Exception:
        logout(request)
        return redirect('login')
    
    if profile.role not in ['owner', 'staff']:
        return redirect('dashboard')
    
    from api.models import NewsletterSubscriber
    
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    
    # Get subscribers with filters
    subscribers = NewsletterSubscriber.objects.all().order_by('-subscribed_at')
    
    if status_filter == 'active':
        subscribers = subscribers.filter(is_active=True)
    elif status_filter == 'inactive':
        subscribers = subscribers.filter(is_active=False)
    
    if search_query:
        subscribers = subscribers.filter(
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(subscribers, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics
    total_subscribers = NewsletterSubscriber.objects.count()
    active_subscribers = NewsletterSubscriber.objects.filter(is_active=True).count()
    inactive_subscribers = NewsletterSubscriber.objects.filter(is_active=False).count()
    
    context = {
        'page_obj': page_obj,
        'total_subscribers': total_subscribers,
        'active_subscribers': active_subscribers,
        'inactive_subscribers': inactive_subscribers,
        'status_filter': status_filter,
        'search_query': search_query,
        'is_owner': profile.role == 'owner',
    }
    
    return render(request, 'accounts/subscriber_management.html', context)

@login_required(login_url='login')
def newsletter_management(request):
    """Newsletter management page for admin dashboard"""
    try:
        profile = request.user.profile
    except Exception:
        logout(request)
        return redirect('login')
    
    if profile.role not in ['owner', 'staff']:
        return redirect('dashboard')
    
    from api.models import NewsletterCampaign, NewsletterSubscriber
    
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    
    # Get campaigns with filters
    campaigns = NewsletterCampaign.objects.all().order_by('-created_at')
    
    if status_filter:
        campaigns = campaigns.filter(status=status_filter)
    
    if search_query:
        campaigns = campaigns.filter(
            Q(title__icontains=search_query) |
            Q(subject__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(campaigns, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics
    total_campaigns = NewsletterCampaign.objects.count()
    draft_campaigns = NewsletterCampaign.objects.filter(status='draft').count()
    sent_campaigns = NewsletterCampaign.objects.filter(status='sent').count()
    total_subscribers = NewsletterSubscriber.objects.filter(is_active=True).count()
    
    context = {
        'page_obj': page_obj,
        'total_campaigns': total_campaigns,
        'draft_campaigns': draft_campaigns,
        'sent_campaigns': sent_campaigns,
        'total_subscribers': total_subscribers,
        'status_filter': status_filter,
        'search_query': search_query,
        'is_owner': profile.role == 'owner',
    }
    
    return render(request, 'accounts/newsletter_management.html', context)

@login_required(login_url='login')
def create_newsletter_campaign(request):
    """Create new newsletter campaign"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
    try:
        profile = request.user.profile
    except Exception:
        return JsonResponse({'error': 'User not authenticated'}, status=401)
    
    if profile.role not in ['owner', 'staff']:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        from api.models import NewsletterCampaign
        
        title = request.POST.get('title')
        subject = request.POST.get('subject')
        content = request.POST.get('content')
        
        if not all([title, subject, content]):
            return JsonResponse({'error': 'All fields are required'}, status=400)
        
        campaign = NewsletterCampaign.objects.create(
            title=title,
            subject=subject,
            content=content,
            status='draft'
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Newsletter campaign created successfully',
            'campaign_id': campaign.id
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required(login_url='login')
def send_newsletter_campaign(request, campaign_id):
    """Send newsletter campaign to subscribers"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
    try:
        profile = request.user.profile
    except Exception:
        return JsonResponse({'error': 'User not authenticated'}, status=401)
    
    if profile.role not in ['owner', 'staff']:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        from api.models import NewsletterCampaign, NewsletterSubscriber, CampaignRecipient
        from django.core.mail import send_mail
        from django.conf import settings
        from django.utils import timezone
        
        campaign = NewsletterCampaign.objects.get(id=campaign_id)
        
        if campaign.status != 'draft':
            return JsonResponse({'error': 'Campaign is not in draft status'}, status=400)
        
        # Get active subscribers
        subscribers = NewsletterSubscriber.objects.filter(is_active=True)
        
        if not subscribers.exists():
            return JsonResponse({'error': 'No active subscribers found'}, status=400)
        
        sent_count = 0
        failed_count = 0
        
        for subscriber in subscribers:
            try:
                # Create campaign recipient record
                recipient = CampaignRecipient.objects.create(
                    campaign=campaign,
                    subscriber=subscriber
                )
                
                # Send email
                send_mail(
                    subject=campaign.subject,
                    message=campaign.content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[subscriber.email],
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
        
        return JsonResponse({
            'success': True,
            'message': f'Campaign sent successfully! {sent_count} emails sent, {failed_count} failed.',
            'sent_count': sent_count,
            'failed_count': failed_count
        })
        
    except NewsletterCampaign.DoesNotExist:
        return JsonResponse({'error': 'Campaign not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500) 