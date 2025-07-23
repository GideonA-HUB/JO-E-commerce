# Stripe Payment Integration Setup

## 🛒 **Online Ordering System with Stripe**

Your Jojo Chopshouse website now has a complete online ordering system with Stripe payment integration!

## 📋 **Features Implemented**

### ✅ **Shopping Cart**
- Add/remove items from cart
- Quantity controls
- Real-time total calculation
- Persistent cart state

### ✅ **Checkout Process**
- 3-step checkout (Customer Info → Delivery Info → Payment)
- Form validation
- Progress indicators

### ✅ **Stripe Payment Integration**
- Secure card processing
- Real-time payment validation
- Payment confirmation emails
- Order status tracking

### ✅ **Order Management**
- Order creation and storage
- Order items tracking
- Status updates (Pending → Confirmed → Preparing → Ready → Delivered)
- Admin dashboard for order management

## 🔧 **Setup Instructions**

### 1. **Get Stripe Keys**
1. Sign up at [stripe.com](https://stripe.com)
2. Go to Dashboard → Developers → API Keys
3. Copy your **Publishable Key** and **Secret Key**

### 2. **Update Settings**
Edit `backend/backend/settings.py`:
```python
# Stripe settings
STRIPE_PUBLISHABLE_KEY = 'pk_test_your_actual_publishable_key'
STRIPE_SECRET_KEY = 'sk_test_your_actual_secret_key'
STRIPE_WEBHOOK_SECRET = 'whsec_your_webhook_secret'  # Optional for now
```

### 3. **Update Frontend**
Edit `js/app.js` line 77:
```javascript
this.stripe = Stripe('pk_test_your_actual_publishable_key');
```

### 4. **Run Migrations**
```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

### 5. **Start the Server**
```bash
# Terminal 1 - Backend
cd backend
python manage.py runserver

# Terminal 2 - Frontend (if using live server)
# Open index.html in browser
```

## 🧪 **Testing**

### **Test Card Numbers**
- **Success**: `4242 4242 4242 4242`
- **Decline**: `4000 0000 0000 0002`
- **Expiry**: Any future date
- **CVC**: Any 3 digits

### **Test Flow**
1. Add items to cart
2. Click checkout
3. Fill customer information
4. Fill delivery information
5. Enter test card details
6. Complete payment

## 📧 **Email Notifications**

The system automatically sends:
- **Order confirmation** to customer
- **New order notification** to admin
- **Contact form notifications** to admin

## 🔒 **Security Features**

- ✅ Stripe Elements for secure card input
- ✅ Server-side payment processing
- ✅ Webhook verification (optional)
- ✅ Input validation
- ✅ CSRF protection

## 📊 **Admin Dashboard**

Access at `http://127.0.0.1:8000/admin/` to:
- View all orders
- Update order status
- Manage products
- View contact messages

## 🚀 **Next Steps**

1. **Get real Stripe keys** for production
2. **Set up webhook endpoint** for real-time updates
3. **Configure email settings** for notifications
4. **Add order tracking** for customers
5. **Implement inventory management**

## 🆘 **Troubleshooting**

### **Payment Not Working**
- Check Stripe keys are correct
- Verify card details are valid
- Check browser console for errors
- Ensure backend server is running

### **Orders Not Creating**
- Check database migrations
- Verify API endpoints are accessible
- Check Django admin for errors

### **Emails Not Sending**
- Verify email settings in Django
- Check Gmail app password is correct
- Test with different email provider

## 📞 **Support**

If you need help:
1. Check the browser console for errors
2. Check Django server logs
3. Verify all settings are correct
4. Test with different browsers

---

**🎉 Your online ordering system is ready! Customers can now place orders and pay securely through your website.** 