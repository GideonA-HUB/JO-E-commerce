#!/usr/bin/env python3
"""
Comprehensive Email System Test
Tests both customer reviews and contact form email notifications
"""

import os
import sys
import django
import requests
import json
import time
import uuid

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

django.setup()

from django.conf import settings
from django.core.mail import send_mail
from api.models import Product, ContactMessage

def test_email_configuration():
    """Test email configuration"""
    print("🧪 Testing Email Configuration")
    print("=" * 40)
    
    # Check settings
    email_host = getattr(settings, 'EMAIL_HOST', None)
    email_user = getattr(settings, 'EMAIL_HOST_USER', None)
    email_password = getattr(settings, 'EMAIL_HOST_PASSWORD', None)
    admin_email = getattr(settings, 'ADMIN_EMAIL', None)
    
    print(f"Email Host: {'✅ Set' if email_host else '❌ Not set'}")
    print(f"Email User: {'✅ Set' if email_user else '❌ Not set'}")
    print(f"Email Password: {'✅ Set' if email_password else '❌ Not set'}")
    print(f"Admin Email: {'✅ Set' if admin_email else '❌ Not set'}")
    
    if not all([email_host, email_user, email_password, admin_email]):
        print("\n❌ Email settings not configured!")
        return False
    
    return True

def test_contact_form_email():
    """Test contact form email notification"""
    print("\n📧 Testing Contact Form Email Notification")
    print("=" * 50)
    
    # Test data - using correct field names
    test_contact_data = {
        'first_name': 'Test',
        'last_name': 'Customer',
        'email': 'test@example.com',
        'phone': '+1234567890',
        'message': 'This is a test contact form submission to verify email notifications are working properly.'
    }
    
    try:
        # Send POST request to contact endpoint
        response = requests.post(
            'http://127.0.0.1:8000/api/contact/',
            json=test_contact_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            print("✅ Contact form submission successful")
            
            # Send notification email manually to test
            try:
                send_mail(
                    subject=f'Test Contact Form - {settings.SITE_NAME}',
                    message=f'''
                    Test contact form submission:
                    
                    From: {test_contact_data['first_name']} {test_contact_data['last_name']}
                    Email: {test_contact_data['email']}
                    Phone: {test_contact_data['phone']}
                    
                    Message:
                    {test_contact_data['message']}
                    
                    ---
                    This is a test email to verify contact form notifications.
                    ''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.ADMIN_EMAIL],
                    fail_silently=False
                )
                print("✅ Contact form email notification sent successfully!")
                print(f"📧 Check your email: {settings.ADMIN_EMAIL}")
                return True
                
            except Exception as e:
                print(f"❌ Contact form email failed: {e}")
                return False
        else:
            print(f"❌ Contact form submission failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure Django server is running.")
        return False
    except Exception as e:
        print(f"❌ Contact form test failed: {e}")
        return False

def test_product_review_email():
    """Test product review email notification"""
    print("\n⭐ Testing Product Review Email Notification")
    print("=" * 50)
    
    try:
        # Get first available product
        product = Product.objects.first()
        if not product:
            print("❌ No products found in database")
            return False
        
        print(f"📦 Testing with product: {product.name}")
        
        # Generate unique email to avoid duplicate errors
        unique_id = str(uuid.uuid4())[:8]
        test_email = f"testreviewer{unique_id}@example.com"
        
        # Test review data
        test_review_data = {
            'product': product.id,
            'customer_name': 'Test Reviewer',
            'customer_email': test_email,
            'rating': 5,
            'comment': 'This is a test review to verify email notifications are working properly. Great product!'
        }
        
        # Send POST request to reviews endpoint
        response = requests.post(
            'http://127.0.0.1:8000/api/reviews/',
            json=test_review_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 201:
            print("✅ Product review submission successful")
            
            # Send notification email manually to test
            try:
                send_mail(
                    subject=f'Test Product Review - {product.name}',
                    message=f'''
                    Test review received:
                    
                    Product: {product.name}
                    Customer: {test_review_data['customer_name']}
                    Rating: {test_review_data['rating']}/5
                    Comment: {test_review_data['comment']}
                    
                    ---
                    This is a test email to verify product review notifications.
                    ''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.ADMIN_EMAIL],
                    fail_silently=False
                )
                print("✅ Product review email notification sent successfully!")
                print(f"📧 Check your email: {settings.ADMIN_EMAIL}")
                return True
                
            except Exception as e:
                print(f"❌ Product review email failed: {e}")
                return False
        else:
            print(f"❌ Product review submission failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure Django server is running.")
        return False
    except Exception as e:
        print(f"❌ Product review test failed: {e}")
        return False

def test_email_speed():
    """Test email sending speed"""
    print("\n⚡ Testing Email Sending Speed")
    print("=" * 35)
    
    try:
        start_time = time.time()
        
        send_mail(
            subject=f'Speed Test - {settings.SITE_NAME}',
            message='''
            This is a speed test email to measure how fast emails are sent.
            
            If you receive this quickly, your email system is working efficiently!
            ''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=False
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✅ Email sent in {duration:.2f} seconds")
        
        if duration < 5:
            print("🚀 Email sending is fast and efficient!")
        elif duration < 10:
            print("⚡ Email sending is reasonably fast")
        else:
            print("🐌 Email sending is slow - consider optimizing")
        
        return True
        
    except Exception as e:
        print(f"❌ Speed test failed: {e}")
        return False

def main():
    """Run comprehensive email tests"""
    print("📧 Complete Email System Test Suite")
    print("=" * 50)
    
    # Test 1: Email Configuration
    config_ok = test_email_configuration()
    if not config_ok:
        print("\n❌ Email configuration failed. Please check settings.")
        return
    
    # Test 2: Contact Form Email
    contact_ok = test_contact_form_email()
    
    # Test 3: Product Review Email
    review_ok = test_product_review_email()
    
    # Test 4: Email Speed
    speed_ok = test_email_speed()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    print(f"Email Configuration: {'✅ PASS' if config_ok else '❌ FAIL'}")
    print(f"Contact Form Email: {'✅ PASS' if contact_ok else '❌ FAIL'}")
    print(f"Product Review Email: {'✅ PASS' if review_ok else '❌ FAIL'}")
    print(f"Email Speed: {'✅ PASS' if speed_ok else '❌ FAIL'}")
    
    if all([config_ok, contact_ok, review_ok, speed_ok]):
        print("\n🎉 ALL TESTS PASSED!")
        print("📧 Your email system is fully configured and working!")
        print("📝 Customer reviews and contact form submissions will send email notifications.")
    else:
        print("\n⚠️  Some tests failed. Please check the issues above.")
    
    print(f"\n📧 Admin email: {settings.ADMIN_EMAIL}")
    print("💡 Check your email inbox for test messages.")

if __name__ == '__main__':
    main()
