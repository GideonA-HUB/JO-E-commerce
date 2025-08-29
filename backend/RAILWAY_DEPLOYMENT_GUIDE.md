# 🚀 Railway Deployment Guide for TASTY FINGERS

## 🚨 **CRITICAL: Fixing 301 Redirect Issues**

Your Railway deployment is experiencing 301 redirects because of SSL redirect settings. This guide will fix these issues.

## 📋 **Current Issues**
1. **301 Redirects**: Caused by `SECURE_SSL_REDIRECT = True` in production
2. **502 Errors**: Server configuration issues
3. **SSL Handling**: Railway handles HTTPS, but Django was trying to redirect

## ✅ **Solution: Updated Railway Configuration**

### **Step 1: Update Railway Environment Variables**

In your Railway dashboard, update these environment variables:

```bash
# Core Settings
DEBUG=False
SECURE_SSL_REDIRECT=False
CORS_ALLOW_ALL_ORIGINS=False

# Hosts and CORS
ALLOWED_HOSTS=tasty-fingers.up.railway.app,localhost,127.0.0.1,0.0.0.0
CORS_ALLOWED_ORIGINS=https://tasty-fingers.up.railway.app,http://localhost:3000

# Database (keep your existing DATABASE_URL)
DATABASE_URL=YOUR_DATABASE_URL_HERE

# Email (keep your existing settings)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=YOUR_EMAIL_HERE
EMAIL_HOST_PASSWORD=YOUR_APP_PASSWORD_HERE
DEFAULT_FROM_EMAIL=YOUR_EMAIL_HERE
ADMIN_EMAIL=YOUR_EMAIL_HERE

# Site Settings
SITE_NAME=TASTY FINGERS
SITE_URL=https://tasty-fingers.up.railway.app

# Cloudinary (keep your existing settings)
CLOUDINARY_CLOUD_NAME=YOUR_CLOUDINARY_CLOUD_NAME
CLOUDINARY_API_KEY=YOUR_CLOUDINARY_API_KEY
CLOUDINARY_API_SECRET=YOUR_CLOUDINARY_API_SECRET

# Security
SECRET_KEY=YOUR_SECRET_KEY_HERE

# Port (Railway will set this automatically)
PORT=3000
```

### **Step 2: Update Build Command**

In Railway dashboard, set the **Build Command** to:

```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput
```

### **Step 3: Update Start Command**

In Railway dashboard, set the **Start Command** to:

```bash
python railway_start_simple.py
```

## 🔧 **Alternative: Manual Commands**

If you prefer to use the original commands, update them to:

### **Build Command:**
```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput
```

### **Start Command:**
```bash
python test_db.py && python manage.py migrate && python manage.py collectstatic --noinput && python manage.py add_sample_data && gunicorn backend.wsgi --config railway_gunicorn.conf.py --bind 0.0.0.0:3000 --workers 1 --timeout 120 --log-level info
```

## 📁 **Files Created for Railway**

### 1. **Railway Settings** (`backend/railway_settings.py`)
- Optimized for Railway deployment
- Disables SSL redirects
- Proper CORS configuration
- Enhanced logging

### 2. **Railway Gunicorn Config** (`backend/railway_gunicorn.conf.py`)
- Railway-specific gunicorn settings
- Proper proxy handling
- Enhanced logging

### 3. **Railway Startup Script** (`backend/railway_start.py`)
- Automated deployment process
- Error handling
- Proper environment setup

## 🚀 **Deployment Steps**

### **Option 1: Use Railway Startup Script (Recommended)**

1. **Update Environment Variables** in Railway dashboard
2. **Set Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
3. **Set Start Command**: `python railway_start_simple.py`
4. **Deploy**

### **Option 2: Use Manual Commands**

1. **Update Environment Variables** in Railway dashboard
2. **Set Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
3. **Set Start Command**: `python test_db.py && python manage.py migrate && python manage.py collectstatic --noinput && python manage.py add_sample_data && gunicorn backend.wsgi --config railway_gunicorn.conf.py --bind 0.0.0.0:3000 --workers 1 --timeout 120 --log-level info`
4. **Deploy**

## 🔍 **Verification Steps**

After deployment, check:

1. **Visit your Railway URL**: `https://tasty-fingers.up.railway.app`
2. **Check for 301 redirects**: Should load directly
3. **Test API endpoints**: `https://tasty-fingers.up.railway.app/api/`
4. **Check admin panel**: `https://tasty-fingers.up.railway.app/admin/`

## 🐛 **Troubleshooting**

### **Still Getting 301 Redirects?**
1. Verify `SECURE_SSL_REDIRECT=False` in environment variables
2. Check that you're using the Railway startup script
3. Ensure all environment variables are set correctly

### **502 Bad Gateway?**
1. Check Railway logs for errors
2. Verify database connection
3. Ensure all dependencies are installed

### **Database Connection Issues?**
1. Verify `DATABASE_URL` is correct
2. Check if database is accessible
3. Run `python test_db.py` to test connection

## 📊 **Expected Results**

After successful deployment:
- ✅ **No 301 redirects** on main pages
- ✅ **Direct access** to API endpoints
- ✅ **Proper HTTPS handling** by Railway
- ✅ **Clean server logs** without redirect warnings
- ✅ **Working admin panel** at `/admin/`

## 🔄 **Monitoring**

Monitor your deployment using:
- **Railway Logs**: Check for errors and warnings
- **Application Logs**: Look for Django and Gunicorn logs
- **Health Checks**: Test your endpoints regularly

## 📞 **Support**

If you continue to experience issues:
1. Check Railway logs for specific error messages
2. Verify all environment variables are set correctly
3. Test locally with the same configuration
4. Contact support with specific error details

## 🔐 **SECURITY IMPORTANT**

Replace all `YOUR_*_HERE` placeholders with your actual secure credentials in Railway environment variables. Never commit actual credentials to version control!

---

**🎯 Goal**: Eliminate 301 redirects and ensure smooth Railway deployment
**✅ Result**: Direct access to your application without unwanted redirects
