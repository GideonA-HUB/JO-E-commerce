from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings
from .models import UserProfile
from api.models import ContactMessage, Order

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
    from django.db.models import Sum  # Ensure Sum is always available
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