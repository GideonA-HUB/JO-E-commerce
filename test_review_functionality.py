#!/usr/bin/env python3
"""
Test Script for TASTY FINGERS Review Functionality
Tests duplicate review prevention and error handling
"""

import requests
import json
import time
from datetime import datetime

class ReviewTester:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name, success, message=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        timestamp = datetime.now().strftime("%H:%M:%S")
        result = f"[{timestamp}] {status} - {test_name}"
        if message:
            result += f": {message}"
        print(result)
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': timestamp
        })
        
    def test_api_endpoint(self, endpoint, method="GET", data=None, expected_status=200):
        """Test API endpoint"""
        url = f"{self.base_url}{endpoint}"
        try:
            if method == "GET":
                response = self.session.get(url)
            elif method == "POST":
                response = self.session.post(url, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            return response
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error testing {endpoint}: {e}")
            return None
            
    def test_products_endpoint(self):
        """Test products endpoint"""
        print("\n🔍 Testing Products Endpoint...")
        response = self.test_api_endpoint("/api/products/")
        
        if response and response.status_code == 200:
            products = response.json()
            self.log_test("Products API", True, f"Found {len(products)} products")
            return products
        else:
            self.log_test("Products API", False, f"Status: {response.status_code if response else 'No response'}")
            return []
            
    def test_product_ratings_endpoint(self, product_id):
        """Test product ratings endpoint"""
        print(f"\n⭐ Testing Product Ratings for Product {product_id}...")
        response = self.test_api_endpoint(f"/api/product-ratings/?product={product_id}")
        
        if response and response.status_code == 200:
            ratings = response.json()
            self.log_test("Product Ratings API", True, f"Found {len(ratings)} ratings")
            return ratings
        else:
            self.log_test("Product Ratings API", False, f"Status: {response.status_code if response else 'No response'}")
            return []
            
    def test_product_comments_endpoint(self, product_id):
        """Test product comments endpoint"""
        print(f"\n💬 Testing Product Comments for Product {product_id}...")
        response = self.test_api_endpoint(f"/api/product-comments/?product={product_id}")
        
        if response and response.status_code == 200:
            comments = response.json()
            self.log_test("Product Comments API", True, f"Found {len(comments)} comments")
            return comments
        else:
            self.log_test("Product Comments API", False, f"Status: {response.status_code if response else 'No response'}")
            return []
            
    def test_submit_rating(self, product_id, user_email, rating, expected_duplicate=False):
        """Test submitting a rating"""
        print(f"\n📝 Testing Rating Submission...")
        
        data = {
            "product": product_id,
            "rating": rating,
            "user_email": user_email
        }
        
        response = self.test_api_endpoint("/api/product-ratings/", method="POST", data=data)
        
        if response:
            if expected_duplicate:
                # Should fail with 400 and specific error message
                if response.status_code == 400:
                    try:
                        error_data = response.json()
                        if "already submitted" in error_data.get('error', ''):
                            self.log_test("Duplicate Rating Prevention", True, "Correctly prevented duplicate rating")
                            return True
                        else:
                            self.log_test("Duplicate Rating Prevention", False, f"Wrong error message: {error_data.get('error')}")
                            return False
                    except Exception as e:
                        # If JSON parsing fails, check the raw text
                        response_text = response.text
                        if "already submitted" in response_text.lower():
                            self.log_test("Duplicate Rating Prevention", True, "Correctly prevented duplicate rating")
                            return True
                        else:
                            self.log_test("Duplicate Rating Prevention", False, f"Could not parse error message: {response_text}")
                            return False
                else:
                    self.log_test("Duplicate Rating Prevention", False, f"Expected 400, got {response.status_code}")
                    return False
            else:
                # Should succeed with 201
                if response.status_code == 201:
                    self.log_test("Rating Submission", True, "Rating submitted successfully")
                    return True
                else:
                    self.log_test("Rating Submission", False, f"Expected 201, got {response.status_code}")
                    return False
        else:
            self.log_test("Rating Submission", False, "No response from server")
            return False
            
    def test_submit_comment(self, product_id, user_email, comment, expected_duplicate=False):
        """Test submitting a comment"""
        print(f"\n📝 Testing Comment Submission...")
        
        data = {
            "product": product_id,
            "comment": comment,
            "user_email": user_email
        }
        
        response = self.test_api_endpoint("/api/product-comments/", method="POST", data=data)
        
        if response:
            if expected_duplicate:
                # Should fail with 400 and specific error message
                if response.status_code == 400:
                    try:
                        error_data = response.json()
                        if "already submitted" in error_data.get('error', ''):
                            self.log_test("Duplicate Comment Prevention", True, "Correctly prevented duplicate comment")
                            return True
                        else:
                            self.log_test("Duplicate Comment Prevention", False, f"Wrong error message: {error_data.get('error')}")
                            return False
                    except Exception as e:
                        # If JSON parsing fails, check the raw text
                        response_text = response.text
                        if "already submitted" in response_text.lower():
                            self.log_test("Duplicate Comment Prevention", True, "Correctly prevented duplicate comment")
                            return True
                        else:
                            self.log_test("Duplicate Comment Prevention", False, f"Could not parse error message: {response_text}")
                            return False
                else:
                    self.log_test("Duplicate Comment Prevention", False, f"Expected 400, got {response.status_code}")
                    return False
            else:
                # Should succeed with 201
                if response.status_code == 201:
                    self.log_test("Comment Submission", True, "Comment submitted successfully")
                    return True
                else:
                    self.log_test("Comment Submission", False, f"Expected 201, got {response.status_code}")
                    return False
        else:
            self.log_test("Comment Submission", False, "No response from server")
            return False
            
    def test_duplicate_review_scenario(self, product_id):
        """Test complete duplicate review scenario"""
        print(f"\n🔄 Testing Complete Duplicate Review Scenario for Product {product_id}...")
        
        test_email = f"test_user_{int(time.time())}@example.com"
        test_rating = 5
        test_comment = "This is a test review for duplicate prevention testing."
        
        # Step 1: Submit initial rating
        print("\n📝 Step 1: Submitting initial rating...")
        rating_success = self.test_submit_rating(product_id, test_email, test_rating, expected_duplicate=False)
        
        # Step 2: Submit initial comment
        print("\n📝 Step 2: Submitting initial comment...")
        comment_success = self.test_submit_comment(product_id, test_email, test_comment, expected_duplicate=False)
        
        # Step 3: Try to submit duplicate rating
        print("\n📝 Step 3: Attempting duplicate rating...")
        duplicate_rating_success = self.test_submit_rating(product_id, test_email, test_rating, expected_duplicate=True)
        
        # Step 4: Try to submit duplicate comment
        print("\n📝 Step 4: Attempting duplicate comment...")
        duplicate_comment_success = self.test_submit_comment(product_id, test_email, test_comment, expected_duplicate=True)
        
        # Step 5: Verify data in database
        print("\n📝 Step 5: Verifying data consistency...")
        ratings = self.test_product_ratings_endpoint(product_id)
        comments = self.test_product_comments_endpoint(product_id)
        
        # Check that only one rating and one comment exist for this user
        # Handle both dictionary and string responses
        user_ratings = []
        user_comments = []
        
        for r in ratings:
            if isinstance(r, dict) and r.get('user_email') == test_email:
                user_ratings.append(r)
            elif isinstance(r, str) and test_email in r:
                user_ratings.append(r)
                
        for c in comments:
            if isinstance(c, dict) and c.get('user_email') == test_email:
                user_comments.append(c)
            elif isinstance(c, str) and test_email in c:
                user_comments.append(c)
        
        data_consistency = len(user_ratings) == 1 and len(user_comments) == 1
        self.log_test("Data Consistency", data_consistency, 
                     f"Found {len(user_ratings)} ratings and {len(user_comments)} comments for test user")
        
        return all([rating_success, comment_success, duplicate_rating_success, 
                   duplicate_comment_success, data_consistency])
                   
    def test_error_message_specificity(self, product_id):
        """Test that error messages are specific and helpful"""
        print(f"\n🎯 Testing Error Message Specificity for Product {product_id}...")
        
        test_email = f"specificity_test_{int(time.time())}@example.com"
        
        # Submit initial review
        self.test_submit_rating(product_id, test_email, 4, expected_duplicate=False)
        self.test_submit_comment(product_id, test_email, "Testing error messages", expected_duplicate=False)
        
        # Try duplicate and check error message
        data = {
            "product": product_id,
            "rating": 5,
            "user_email": test_email
        }
        
        response = self.test_api_endpoint("/api/product-ratings/", method="POST", data=data)
        
        if response and response.status_code == 400:
            try:
                error_data = response.json()
                error_message = error_data.get('error', '')
            except Exception as e:
                error_message = response.text
            
            # Check for specific error message
            if "already submitted" in error_message.lower() and "one rating per product" in error_message.lower():
                self.log_test("Specific Error Messages", True, "Error message is specific and helpful")
                return True
            else:
                self.log_test("Specific Error Messages", False, f"Error message not specific enough: {error_message}")
                return False
        else:
            self.log_test("Specific Error Messages", False, "No error response received")
            return False
            
    def test_multiple_products(self):
        """Test duplicate prevention across multiple products"""
        print(f"\n🔄 Testing Duplicate Prevention Across Multiple Products...")
        
        products = self.test_products_endpoint()
        if not products:
            self.log_test("Multiple Products Test", False, "No products available")
            return False
            
        test_email = f"multi_product_test_{int(time.time())}@example.com"
        success_count = 0
        
        # Test first 3 products
        for i, product in enumerate(products[:3]):
            product_id = product['id']
            print(f"\n📝 Testing Product {i+1}: {product['name']}")
            
            # Submit review to this product
            rating_success = self.test_submit_rating(product_id, test_email, 4, expected_duplicate=False)
            comment_success = self.test_submit_comment(product_id, test_email, f"Review for {product['name']}", expected_duplicate=False)
            
            # Try duplicate
            duplicate_rating_success = self.test_submit_rating(product_id, test_email, 5, expected_duplicate=True)
            duplicate_comment_success = self.test_submit_comment(product_id, test_email, "Duplicate review", expected_duplicate=False)
            
            if all([rating_success, comment_success, duplicate_rating_success, duplicate_comment_success]):
                success_count += 1
                
        self.log_test("Multiple Products Test", success_count == 3, f"{success_count}/3 products passed")
        return success_count == 3
        
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting TASTY FINGERS Review Functionality Tests")
        print("=" * 60)
        
        # Test basic endpoints
        products = self.test_products_endpoint()
        if not products:
            print("❌ Cannot continue tests without products")
            return
            
        # Get first product for testing
        test_product = products[0]
        product_id = test_product['id']
        
        print(f"\n🎯 Using Product: {test_product['name']} (ID: {product_id})")
        
        # Run individual tests
        self.test_product_ratings_endpoint(product_id)
        self.test_product_comments_endpoint(product_id)
        
        # Run comprehensive tests
        self.test_duplicate_review_scenario(product_id)
        self.test_error_message_specificity(product_id)
        self.test_multiple_products()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED! Review functionality is working correctly.")
        else:
            print(f"\n⚠️  {total - passed} TESTS FAILED. Please check the implementation.")
            
        # Print failed tests
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print("\n❌ Failed Tests:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['message']}")
                
        return passed == total

def main():
    """Main function"""
    print("🧪 TASTY FINGERS Review Functionality Test Suite")
    print("This script tests the duplicate review prevention system")
    print()
    
    # Check if server is running
    try:
        response = requests.get("http://127.0.0.1:8000/api/products/", timeout=5)
        if response.status_code != 200:
            print("❌ Server is running but products endpoint is not accessible")
            return
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to server. Please make sure the Django server is running on http://127.0.0.1:8000")
        print("   Run: cd backend && python manage.py runserver")
        return
        
    # Run tests
    tester = ReviewTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ Review system is working correctly!")
        print("   - Duplicate reviews are properly prevented")
        print("   - Error messages are specific and helpful")
        print("   - Data consistency is maintained")
    else:
        print("\n❌ Review system has issues that need to be fixed")
        
    return success

if __name__ == "__main__":
    main()
