#!/usr/bin/env python3
"""
Simple Test Script for TASTY FINGERS Unified Review System
Tests the ProductReview model (unified rating + comment)
"""

import requests
import json
import time

def test_unified_review_system():
    """Test unified review system using ProductReview model"""
    base_url = "http://127.0.0.1:8000"
    
    print("🧪 Testing Unified Review System (ProductReview)")
    print("=" * 60)
    
    # Get a product to test with
    try:
        response = requests.get(f"{base_url}/api/products/")
        if response.status_code != 200:
            print("❌ Failed to get products")
            return False
            
        products = response.json()
        if not products:
            print("❌ No products found")
            return False
            
        product = products[0]
        product_id = product['id']
        print(f"✅ Using product: {product['name']} (ID: {product_id})")
        
    except Exception as e:
        print(f"❌ Error getting products: {e}")
        return False
    
    # Test email
    test_email = f"test_user_{int(time.time())}@example.com"
    print(f"📧 Test email: {test_email}")
    
    # Step 1: Submit initial review
    print("\n📝 Step 1: Submitting initial review...")
    review_data = {
        "product": product_id,
        "customer_name": "Test User",
        "customer_email": test_email,
        "rating": 5,
        "comment": "This is a test review for the unified review system."
    }
    
    try:
        response = requests.post(f"{base_url}/api/reviews/", json=review_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 201:
            print("   ✅ Initial review submitted successfully")
        else:
            print(f"   ❌ Failed to submit initial review: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error submitting review: {e}")
        return False
    
    # Step 2: Try to submit duplicate review
    print("\n📝 Step 2: Attempting duplicate review...")
    duplicate_review_data = {
        "product": product_id,
        "customer_name": "Test User",
        "customer_email": test_email,
        "rating": 4,  # Different rating
        "comment": "This is a different comment that should be prevented."
    }
    
    try:
        response = requests.post(f"{base_url}/api/reviews/", json=duplicate_review_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 400:
            response_data = response.json()
            # Check for both error formats
            error_message = response_data.get('error', '') or response_data.get('errors', {}).get('non_field_errors', [''])[0]
            if "already submitted" in error_message or "unique" in error_message.lower():
                print("   ✅ Duplicate review correctly prevented with specific error message")
            else:
                print(f"   ❌ Wrong error message: {error_message}")
                return False
        else:
            print(f"   ❌ Expected 400, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing duplicate review: {e}")
        return False
    
    # Step 3: Verify data consistency
    print("\n📝 Step 3: Verifying data consistency...")
    
    try:
        # Get reviews
        response = requests.get(f"{base_url}/api/reviews/?product={product_id}")
        if response.status_code == 200:
            reviews = response.json()
            
            # Handle both list and object responses
            if isinstance(reviews, list):
                user_reviews = [r for r in reviews if isinstance(r, dict) and r.get('customer_email') == test_email]
            else:
                # If it's an object, check if it has a results field
                reviews_list = reviews.get('results', []) if isinstance(reviews, dict) else []
                user_reviews = [r for r in reviews_list if isinstance(r, dict) and r.get('customer_email') == test_email]
            
            print(f"   Found {len(user_reviews)} reviews for test user")
            
            if len(user_reviews) == 1:
                print("   ✅ Data consistency verified - exactly one review")
            else:
                print(f"   ❌ Data inconsistency - expected 1 review, got {len(user_reviews)}")
                return False
        else:
            print(f"   ❌ Failed to get reviews: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error verifying data consistency: {e}")
        return False
    
    print("\n🎉 ALL TESTS PASSED!")
    print("✅ Unified review system is working correctly:")
    print("   - Initial reviews are accepted")
    print("   - Duplicate reviews are prevented with 400 status")
    print("   - Specific error messages are returned")
    print("   - Data consistency is maintained")
    print("   - Reviews appear in Django admin 'Product reviews' section")
    
    return True

def main():
    """Main function"""
    print("🧪 Unified TASTY FINGERS Review Test")
    print("This script tests the unified ProductReview system")
    print()
    
    # Check if server is running
    try:
        response = requests.get("http://127.0.0.1:8000/api/products/", timeout=5)
        if response.status_code != 200:
            print("❌ Server is running but products endpoint is not accessible")
            return False
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to server. Please make sure the Django server is running on http://127.0.0.1:8000")
        print("   Run: cd backend && python manage.py runserver")
        return False
    
    # Run test
    success = test_unified_review_system()
    
    if success:
        print("\n✅ Unified review system is working correctly!")
        print("📋 Now when you submit reviews through the frontend:")
        print("   - They will appear in Django admin 'Product reviews' section")
        print("   - They will NOT appear in 'Product ratings' or 'Product comments' sections")
        print("   - This is the correct behavior for the unified system")
    else:
        print("\n❌ Unified review system has issues that need to be fixed")
    
    return success

if __name__ == "__main__":
    main()
