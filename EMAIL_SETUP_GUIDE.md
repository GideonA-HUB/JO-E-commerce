# 📧 Email Notifications Setup Guide

## **Email Notifications Implemented!**

Your contact form now sends email notifications when customers submit messages. Here's how to configure it:

---

## **Step 1: Set Up Gmail App Password**

### **1. Enable 2-Factor Authentication**
1. Go to your Google Account: https://myaccount.google.com/
2. Click "Security" in the left sidebar
3. Under "Signing in to Google," click "2-Step Verification"
4. Follow the steps to enable it

### **2. Generate App Password**
1. Go back to Security settings
2. Under "2-Step Verification," click "App passwords"
3. Select "Mail" and "Windows Computer"
4. Click "Generate"
5. Copy the 16-character password (e.g., `abcd efgh ijkl mnop`)

---

## **Step 2: Update Django Settings**

Edit `backend/backend/settings.py` and update these lines:

```python
# Email settings for customer responses
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-actual-email@gmail.com'  # Your Gmail address
EMAIL_HOST_PASSWORD = 'your-16-digit-app-password'  # The app password you generated
DEFAULT_FROM_EMAIL = 'your-actual-email@gmail.com'  # Your Gmail address

# Email notification settings
ADMIN_EMAIL = 'your-actual-email@gmail.com'  # Where you want notifications
SITE_NAME = 'CHOPHOUSE'  # Your restaurant name
```

**Replace:**
- `your-actual-email@gmail.com` with your real Gmail address
- `your-16-digit-app-password` with the app password from Step 1

---

## **Step 3: Test Email Notifications**

Run the test script:
```cmd
python test_email_notifications.py
```

**Expected Output:**
```
📧 Email Notification Test Suite
==================================================
🧪 Testing Email Configuration
========================================
Email Host: ✅ Set
Email User: ✅ Set
Email Password: ✅ Set
Admin Email: ✅ Set

📧 Testing Email Sending...
✅ Test email sent successfully!
📧 Check your email: your-email@gmail.com

🎉 Email notifications are working!
📝 Contact form submissions will now send email notifications.
```

---

## **Step 4: Test Contact Form**

1. Go to http://127.0.0.1:8000/
2. Fill out the contact form
3. Submit it
4. Check your email for the notification

**You should receive an email like this:**
```
Subject: New Contact Form: John Doe

New contact form submission received:

Name: John Doe
Email: john@example.com
Phone: 123-456-7890
IP Address: 192.168.1.100
Date: 2024-07-13 14:30:00
Message ID: 1

Message:
I need catering for 50 people for my wedding next month. Can you help?

---
This message was sent automatically from your CHOPHOUSE website contact form.
You can reply directly to john@example.com to respond to the customer.
```

---

## **Troubleshooting**

### **If Email Test Fails:**

#### **1. Check Gmail Settings**
- ✅ 2-factor authentication enabled
- ✅ App password generated correctly
- ✅ App password copied without spaces

#### **2. Check Django Settings**
- ✅ EMAIL_HOST_USER is your Gmail address
- ✅ EMAIL_HOST_PASSWORD is the 16-character app password
- ✅ ADMIN_EMAIL is set correctly

#### **3. Common Error Messages**

**"Authentication failed"**
- App password is incorrect
- 2-factor authentication not enabled

**"Username and Password not accepted"**
- Gmail address is wrong
- App password has extra spaces

**"Connection refused"**
- Check internet connection
- Gmail SMTP server might be temporarily down

---

## **Alternative Email Providers**

### **Outlook/Hotmail:**
```python
EMAIL_HOST = 'smtp-mail.outlook.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
```

### **Yahoo:**
```python
EMAIL_HOST = 'smtp.mail.yahoo.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
```

### **Custom SMTP:**
```python
EMAIL_HOST = 'your-smtp-server.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
```

---

## **Benefits of Email Notifications**

✅ **Works with any Python version**  
✅ **No external dependencies**  
✅ **Professional and reliable**  
✅ **You can reply directly to customers**  
✅ **Works on all devices**  
✅ **No account bans or restrictions**  
✅ **Production-ready**  

---

## **Next Steps**

1. **Configure your email settings** (Step 2 above)
2. **Test the email functionality** (Step 3 above)
3. **Test the contact form** (Step 4 above)
4. **Start receiving notifications!**

**Your contact form will now send you email notifications for every submission!** 🎉 