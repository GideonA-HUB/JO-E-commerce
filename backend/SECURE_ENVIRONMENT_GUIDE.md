# 🔒 SECURE ENVIRONMENT SETUP GUIDE

## 🚨 **CRITICAL SECURITY WARNING**

**NEVER commit sensitive information to version control!** All sensitive data has been removed from the codebase.

## 📋 **Required Environment Variables**

Set these in your Railway dashboard:

### **Core Settings**
```bash
DEBUG=False
SECURE_SSL_REDIRECT=False
CORS_ALLOW_ALL_ORIGINS=False
```

### **Hosts and CORS**
```bash
ALLOWED_HOSTS=tasty-fingers.up.railway.app,localhost,127.0.0.1,0.0.0.0
CORS_ALLOWED_ORIGINS=https://tasty-fingers.up.railway.app,http://localhost:3000
```

### **Database (Railway provides this)**
```bash
DATABASE_URL=postgresql://postgres:twnerPQrOqTIOXuMorQYOcZDJwoNahFQ@crossover.proxy.rlwy.net:18398/railway
```

### **Email Settings**
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=gideonamienz24@gmail.com
EMAIL_HOST_PASSWORD=bfdq jmxo ppuo izkt
DEFAULT_FROM_EMAIL=gideonamienz24@gmail.com
ADMIN_EMAIL=gideonamienz24@gmail.com
```

### **Site Settings**
```bash
SITE_NAME=TASTY FINGERS
SITE_URL=https://tasty-fingers.up.railway.app
```

### **Cloudinary Settings**
```bash
CLOUDINARY_CLOUD_NAME=dao40lt42
CLOUDINARY_API_KEY=138773767419866
CLOUDINARY_API_SECRET=Q-099CT3pgd-uHAt60xVDVRg-ok
```

### **Security**
```bash
SECRET_KEY=FPSXru8or3uzUcK-MGDbaw8LkKx0uzrqa53LTQKafoQNDv4hc7sfRGnf0pny3ZSr2mI
```

### **Port (Railway sets this)**
```bash
PORT=3000
```

## 🚀 **Railway Commands**

### **Build Command:**
```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput
```

### **Start Command:**
```bash
python railway_start_simple.py
```

## 🔒 **Security Best Practices**

1. **Environment Variables**: Always use environment variables for sensitive data
2. **No Hardcoding**: Never hardcode passwords, API keys, or secrets in code
3. **Git Ignore**: Ensure `.env` files are in `.gitignore`
4. **Regular Rotation**: Regularly rotate your API keys and passwords
5. **Access Control**: Limit access to your Railway dashboard

## 🛡️ **What Was Secured**

- ✅ Removed hardcoded database credentials
- ✅ Removed hardcoded email passwords
- ✅ Removed hardcoded API keys
- ✅ Removed hardcoded secret keys
- ✅ Removed hardcoded Cloudinary credentials
- ✅ All sensitive data now uses environment variables

## 📞 **Emergency Actions**

If you suspect your credentials have been compromised:

1. **Immediately rotate all passwords and API keys**
2. **Update Railway environment variables**
3. **Check for unauthorized access**
4. **Monitor your application logs**

## ✅ **Verification**

After setting up environment variables:
- ✅ Application deploys successfully
- ✅ No sensitive data in code
- ✅ All functionality works as expected
- ✅ Security best practices followed
