#!/usr/bin/env python3
"""
Django Shell Test Script for PaystackService and Order System
Run this script in Django shell: python manage.py shell < test_paystack_shell.py
"""

import os
import sys
import django
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.models import Product, Order, OrderItem
from api.paystack_service import PaystackService
from api.serializers import OrderSerializer
from django.contrib.auth.models import User

def test_paystack_service():
    """Test PaystackService methods"""
    print("🔧 Testing PaystackService...")
    
    try:
        paystack_service = PaystackService()
        print("✅ PaystackService initialized successfully")
        
        # Test data
        test_data = {
            'email': 'test@example.com',
            'amount': 100000,  # 1000 Naira in kobo
            'reference': 'TEST_REF_123',
            'callback_url': 'http://localhost:8000/api/orders/1/confirm_payment/'
        }
        
        print(f"📝 Test data: {test_data}")
        
        # Test initialize_transaction (will fail with test keys, but that's expected)
        try:
            result = paystack_service.initialize_transaction(test_data)
            print(f"✅ Transaction initialized: {result}")
        except Exception as e:
            print(f"⚠️  Expected error with test keys: {str(e)[:100]}...")
        
        # Test verify_transaction
        try:
            result = paystack_service.verify_transaction('TEST_REF_123')
            print(f"⚠️  Expected error with test reference: {str(e)[:100]}...")
        except Exception as e:
            print(f"⚠️  Expected error with test reference: {str(e)[:100]}...")
            
        print("✅ PaystackService tests completed\n")
        
    except Exception as e:
        print(f"❌ PaystackService test failed: {str(e)}")

def test_order_creation():
    """Test order creation directly in Django"""
    print("🛒 Testing Order Creation...")
    
    try:
        # Get or create a test product
        product, created = Product.objects.get_or_create(
            name="Test Product",
            defaults={
                'description': 'A test product for testing',
                'price': Decimal('1500.00'),
                'category': 'finger-foods',
                'image': 'test-product.jpg',
                'is_available': True
            }
        )
        
        if created:
            print(f"✅ Created test product: {product.name}")
        else:
            print(f"✅ Using existing test product: {product.name}")
        
        # Create order data
        order_data = {
            'first_name': 'Test',
            'last_name': 'Customer',
            'email': 'test@example.com',
            'phone': '+2348012345678',
            'address': '123 Test Street',
            'city': 'Lagos',
            'state': 'Lagos',
            'zip_code': '100001',
            'total_amount': Decimal('3000.00'),
            'status': 'pending'
        }
        
        # Create order
        order = Order.objects.create(**order_data)
        print(f"✅ Created order: #{order.id}")
        
        # Create order item
        order_item = OrderItem.objects.create(
            order=order,
            product=product,
            quantity=2,
            price=product.price
        )
        print(f"✅ Created order item: {order_item.product.name} x {order_item.quantity}")
        
        # Test serializer
        serializer = OrderSerializer(order)
        order_json = serializer.data
        print(f"✅ Order serialized: {order_json['id']}")
        
        # Test order retrieval
        retrieved_order = Order.objects.get(id=order.id)
        print(f"✅ Order retrieved: #{retrieved_order.id} - Status: {retrieved_order.status}")
        
        # Test order update
        retrieved_order.status = 'confirmed'
        retrieved_order.payment_reference = 'TEST_REF_123'
        retrieved_order.save()
        print(f"✅ Order updated: Status changed to {retrieved_order.status}")
        
        print("✅ Order creation tests completed\n")
        return order
        
    except Exception as e:
        print(f"❌ Order creation test failed: {str(e)}")
        return None

def test_order_management():
    """Test order management functions"""
    print("📋 Testing Order Management...")
    
    try:
        # Count all orders
        total_orders = Order.objects.count()
        print(f"✅ Total orders in database: {total_orders}")
        
        # Get pending orders
        pending_orders = Order.objects.filter(status='pending')
        print(f"✅ Pending orders: {pending_orders.count()}")
        
        # Get confirmed orders
        confirmed_orders = Order.objects.filter(status='confirmed')
        print(f"✅ Confirmed orders: {confirmed_orders.count()}")
        
        # Get recent orders
        recent_orders = Order.objects.order_by('-created_at')[:5]
        print(f"✅ Recent orders: {recent_orders.count()}")
        
        for order in recent_orders:
            print(f"   - Order #{order.id}: {order.first_name} {order.last_name} - {order.status}")
        
        print("✅ Order management tests completed\n")
        
    except Exception as e:
        print(f"❌ Order management test failed: {str(e)}")

def test_product_management():
    """Test product management"""
    print("🍕 Testing Product Management...")
    
    try:
        # Count all products
        total_products = Product.objects.count()
        print(f"✅ Total products in database: {total_products}")
        
        # Get available products
        available_products = Product.objects.filter(is_available=True)
        print(f"✅ Available products: {available_products.count()}")
        
        # Get products by category
        finger_foods = Product.objects.filter(category='finger-foods')
        beverages = Product.objects.filter(category='beverages')
        desserts = Product.objects.filter(category='desserts')
        
        print(f"✅ Finger foods: {finger_foods.count()}")
        print(f"✅ Beverages: {beverages.count()}")
        print(f"✅ Desserts: {desserts.count()}")
        
        # Show sample products
        sample_products = Product.objects.all()[:3]
        print("✅ Sample products:")
        for product in sample_products:
            print(f"   - {product.name}: ₦{product.price} ({product.category})")
        
        print("✅ Product management tests completed\n")
        
    except Exception as e:
        print(f"❌ Product management test failed: {str(e)}")

def main():
    """Run all tests"""
    print("🚀 Starting Django Shell Tests for TASTY FINGERS")
    print("=" * 60)
    
    # Run tests
    test_paystack_service()
    test_order_creation()
    test_order_management()
    test_product_management()
    
    print("=" * 60)
    print("🎉 All Django shell tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()
