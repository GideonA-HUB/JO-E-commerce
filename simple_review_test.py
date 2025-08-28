#!/usr/bin/env python3
"""
Simple Test Script for TASTY FINGERS Review Functionality
Tests duplicate review prevention with detailed logging
"""

import requests
import json
import time

def test_duplicate_prevention():
    """Test duplicate review prevention"""
    base_url = "http://127.0.0.1:8000"
    
    print("🧪 Testing Duplicate Review Prevention")
    print("=" * 50)
    
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
    
    # Step 1: Submit initial rating
    print("\n📝 Step 1: Submitting initial rating...")
    rating_data = {
        "product": product_id,
        "rating": 5,
        "user_email": test_email
    }
    
    try:
        response = requests.post(f"{base_url}/api/product-ratings/", json=rating_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 201:
            print("   ✅ Initial rating submitted successfully")
        else:
            print(f"   ❌ Failed to submit initial rating: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error submitting rating: {e}")
        return False
    
    # Step 2: Submit initial comment
    print("\n📝 Step 2: Submitting initial comment...")
    comment_data = {
        "product": product_id,
        "comment": "This is a test review for duplicate prevention testing.",
        "user_email": test_email
    }
    
    try:
        response = requests.post(f"{base_url}/api/product-comments/", json=comment_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 201:
            print("   ✅ Initial comment submitted successfully")
        else:
            print(f"   ❌ Failed to submit initial comment: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error submitting comment: {e}")
        return False
    
    # Step 3: Try to submit duplicate rating
    print("\n📝 Step 3: Attempting duplicate rating...")
    duplicate_rating_data = {
        "product": product_id,
        "rating": 4,  # Different rating
        "user_email": test_email
    }
    
    try:
        response = requests.post(f"{base_url}/api/product-ratings/", json=duplicate_rating_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 400:
            response_data = response.json()
            if "already submitted" in response_data.get('error', ''):
                print("   ✅ Duplicate rating correctly prevented with specific error message")
            else:
                print(f"   ❌ Wrong error message: {response_data.get('error')}")
                return False
        else:
            print(f"   ❌ Expected 400, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing duplicate rating: {e}")
        return False
    
    # Step 4: Try to submit duplicate comment
    print("\n📝 Step 4: Attempting duplicate comment...")
    duplicate_comment_data = {
        "product": product_id,
        "comment": "This is a different comment that should be prevented.",
        "user_email": test_email
    }
    
    try:
        response = requests.post(f"{base_url}/api/product-comments/", json=duplicate_comment_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 400:
            response_data = response.json()
            if "already submitted" in response_data.get('error', ''):
                print("   ✅ Duplicate comment correctly prevented with specific error message")
            else:
                print(f"   ❌ Wrong error message: {response_data.get('error')}")
                return False
        else:
            print(f"   ❌ Expected 400, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing duplicate comment: {e}")
        return False
    
    # Step 5: Verify data consistency
    print("\n📝 Step 5: Verifying data consistency...")
    
    try:
        # Get ratings
        response = requests.get(f"{base_url}/api/product-ratings/?product={product_id}")
        if response.status_code == 200:
            ratings = response.json()
            user_ratings = [r for r in ratings if r.get('user_email') == test_email]
            print(f"   Found {len(user_ratings)} ratings for test user")
        else:
            print(f"   ❌ Failed to get ratings: {response.status_code}")
            return False
            
        # Get comments
        response = requests.get(f"{base_url}/api/product-comments/?product={product_id}")
        if response.status_code == 200:
            comments = response.json()
            user_comments = [c for c in comments if c.get('user_email') == test_email]
            print(f"   Found {len(user_comments)} comments for test user")
        else:
            print(f"   ❌ Failed to get comments: {response.status_code}")
            return False
            
        if len(user_ratings) == 1 and len(user_comments) == 1:
            print("   ✅ Data consistency verified - exactly one rating and one comment")
        else:
            print(f"   ❌ Data inconsistency - expected 1 rating and 1 comment, got {len(user_ratings)} ratings and {len(user_comments)} comments")
            return False
            
    except Exception as e:
        print(f"   ❌ Error verifying data consistency: {e}")
        return False
    
    print("\n🎉 ALL TESTS PASSED!")
    print("✅ Duplicate review prevention is working correctly:")
    print("   - Initial reviews are accepted")
    print("   - Duplicate reviews are prevented with 400 status")
    print("   - Specific error messages are returned")
    print("   - Data consistency is maintained")
    
    return True

def main():
    """Main function"""
    print("🧪 Simple TASTY FINGERS Review Test")
    print("This script tests the duplicate review prevention system")
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
    success = test_duplicate_prevention()
    
    if success:
        print("\n✅ Review system is working correctly!")
    else:
        print("\n❌ Review system has issues that need to be fixed")
    
    return success

if __name__ == "__main__":
    main()
