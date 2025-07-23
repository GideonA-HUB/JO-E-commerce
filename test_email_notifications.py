#!/usr/bin/env python3
"""
Test email notifications for contact form
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

django.setup()

from django.conf import settings
from django.core.mail import send_mail

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
        print("\n💡 To configure email notifications:")
        print("1. Update backend/backend/settings.py")
        print("2. Set EMAIL_HOST_USER to your Gmail address")
        print("3. Set EMAIL_HOST_PASSWORD to your Gmail app password")
        print("4. Set ADMIN_EMAIL to where you want notifications")
        return False
    
    return True

def test_email_sending():
    """Test sending a test email"""
    print("\n📧 Testing Email Sending...")
    
    try:
        subject = f"Test Email from {getattr(settings, 'SITE_NAME', 'CHOPHOUSE')}"
        message = """
This is a test email to verify your email notifications are working.

If you receive this email, your contact form notifications will work perfectly!

---
Sent automatically from your CHOPHOUSE website.
        """.strip()
        
        # Send test email
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=False
        )
        
        print("✅ Test email sent successfully!")
        print(f"📧 Check your email: {settings.ADMIN_EMAIL}")
        return True
        
    except Exception as e:
        print(f"❌ Email sending failed: {e}")
        print("\n💡 Common issues:")
        print("1. Gmail app password not set correctly")
        print("2. 2-factor authentication not enabled")
        print("3. Less secure app access not enabled")
        return False

def main():
    """Run email tests"""
    print("📧 Email Notification Test Suite")
    print("=" * 50)
    
    # Test configuration
    config_ok = test_email_configuration()
    
    if config_ok:
        # Test sending
        sending_ok = test_email_sending()
        
        if sending_ok:
            print("\n🎉 Email notifications are working!")
            print("📝 Contact form submissions will now send email notifications.")
        else:
            print("\n⚠️ Email configuration needs fixing.")
    else:
        print("\n❌ Email settings need to be configured.")

if __name__ == "__main__":
    main() 