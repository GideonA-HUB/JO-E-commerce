# 🚀 SIMPLE RAILWAY COMMANDS

## 🎯 **MOST RELIABLE SOLUTION**

Use these exact commands in your Railway dashboard:

### **Build Command:**
```bash
pip install -r requirements.txt
```

### **Start Command:**
```bash
python manage.py migrate && python manage.py collectstatic --noinput && python manage.py add_sample_data && gunicorn backend.wsgi --bind 0.0.0.0:3000 --workers 1 --timeout 120 --log-level info
```

## 🔧 **Environment Variables**

Make sure these are set in Railway:

```bash
DEBUG=False
SECURE_SSL_REDIRECT=False
CORS_ALLOW_ALL_ORIGINS=False
ALLOWED_HOSTS=tasty-fingers.up.railway.app,localhost,127.0.0.1,0.0.0.0
CORS_ALLOWED_ORIGINS=https://tasty-fingers.up.railway.app,http://localhost:3000
```

## 🚨 **Why This Works**

- ✅ **No external config files** - avoids all configuration errors
- ✅ **Minimal Gunicorn parameters** - only essential settings
- ✅ **Direct commands** - no script complexity
- ✅ **Railway proven** - standard approach for Django on Railway

## 📋 **Steps**

1. **Copy the Build Command** above
2. **Copy the Start Command** above  
3. **Set Environment Variables** in Railway dashboard
4. **Deploy** - Railway will automatically redeploy
5. **Test** your application

## 🎯 **Expected Result**

- ✅ No configuration errors
- ✅ Successful deployment
- ✅ Working application at https://tasty-fingers.up.railway.app
- ✅ No 301 redirects

This is the simplest, most reliable approach that should work immediately!
