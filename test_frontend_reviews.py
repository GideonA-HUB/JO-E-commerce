#!/usr/bin/env python3
"""
Frontend Test Script for TASTY FINGERS Review Functionality
Tests the user interface behavior for duplicate reviews using Selenium
"""

import time
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class FrontendReviewTester:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.driver = None
        self.test_results = []
        
    def setup_driver(self):
        """Setup Chrome driver with options"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in headless mode
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            return True
        except Exception as e:
            print(f"❌ Failed to setup Chrome driver: {e}")
            print("   Make sure Chrome and ChromeDriver are installed")
            return False
            
    def log_test(self, test_name, success, message=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        timestamp = time.strftime("%H:%M:%S")
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
        
    def navigate_to_site(self):
        """Navigate to the main site"""
        try:
            self.driver.get(self.base_url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            self.log_test("Site Navigation", True, "Successfully loaded main site")
            return True
        except Exception as e:
            self.log_test("Site Navigation", False, f"Failed to load site: {e}")
            return False
            
    def find_product_cards(self):
        """Find product cards on the page"""
        try:
            # Wait for products to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "product-card"))
            )
            
            product_cards = self.driver.find_elements(By.CLASS_NAME, "product-card")
            self.log_test("Product Cards Found", True, f"Found {len(product_cards)} product cards")
            return product_cards
        except TimeoutException:
            self.log_test("Product Cards Found", False, "No product cards found within timeout")
            return []
        except Exception as e:
            self.log_test("Product Cards Found", False, f"Error finding product cards: {e}")
            return []
            
    def open_product_modal(self, product_card):
        """Open product modal by clicking view details"""
        try:
            # Find and click the "View Details" button
            view_button = product_card.find_element(By.XPATH, ".//button[contains(text(), 'View Details')]")
            self.driver.execute_script("arguments[0].click();", view_button)
            
            # Wait for modal to appear
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "product-modal"))
            )
            
            self.log_test("Product Modal Open", True, "Successfully opened product modal")
            return True
        except Exception as e:
            self.log_test("Product Modal Open", False, f"Failed to open modal: {e}")
            return False
            
    def check_review_form_visibility(self):
        """Check if review form is visible in modal"""
        try:
            # Look for review form elements
            review_form = self.driver.find_element(By.XPATH, "//div[contains(text(), 'Write a Review')]")
            self.log_test("Review Form Visibility", True, "Review form is visible")
            return True
        except NoSuchElementException:
            self.log_test("Review Form Visibility", False, "Review form not found")
            return False
        except Exception as e:
            self.log_test("Review Form Visibility", False, f"Error checking review form: {e}")
            return False
            
    def test_duplicate_review_ui(self):
        """Test the UI behavior for duplicate reviews"""
        print("\n🔄 Testing Duplicate Review UI Behavior...")
        
        try:
            # Find the info message about already reviewed
            info_message = self.driver.find_element(
                By.XPATH, 
                "//div[contains(text(), 'You have already submitted a review for this product')]"
            )
            
            if info_message.is_displayed():
                self.log_test("Duplicate Review Info Message", True, "Info message is displayed")
                
                # Check if submit button is disabled
                submit_button = self.driver.find_element(
                    By.XPATH, 
                    "//button[contains(text(), 'Submit Review')]"
                )
                
                if submit_button.get_attribute("disabled"):
                    self.log_test("Submit Button Disabled", True, "Submit button is properly disabled")
                    return True
                else:
                    self.log_test("Submit Button Disabled", False, "Submit button should be disabled")
                    return False
            else:
                self.log_test("Duplicate Review Info Message", False, "Info message not displayed")
                return False
                
        except NoSuchElementException:
            self.log_test("Duplicate Review UI Test", False, "Could not find duplicate review UI elements")
            return False
        except Exception as e:
            self.log_test("Duplicate Review UI Test", False, f"Error testing UI: {e}")
            return False
            
    def test_error_message_display(self):
        """Test that error messages are displayed correctly"""
        print("\n🎯 Testing Error Message Display...")
        
        try:
            # Try to submit a review (this should fail if user already reviewed)
            submit_button = self.driver.find_element(
                By.XPATH, 
                "//button[contains(text(), 'Submit Review')]"
            )
            
            if not submit_button.get_attribute("disabled"):
                # If button is not disabled, try to submit
                self.driver.execute_script("arguments[0].click();", submit_button)
                
                # Wait for error message
                time.sleep(2)
                
                error_message = self.driver.find_element(
                    By.XPATH, 
                    "//div[contains(@class, 'text-red-600') or contains(@class, 'text-red-400')]"
                )
                
                if error_message.is_displayed():
                    error_text = error_message.text
                    if "already submitted" in error_text.lower():
                        self.log_test("Error Message Display", True, "Correct error message displayed")
                        return True
                    else:
                        self.log_test("Error Message Display", False, f"Wrong error message: {error_text}")
                        return False
                else:
                    self.log_test("Error Message Display", False, "No error message displayed")
                    return False
            else:
                self.log_test("Error Message Display", True, "Submit button disabled, no error needed")
                return True
                
        except NoSuchElementException:
            self.log_test("Error Message Display", False, "Could not find error message elements")
            return False
        except Exception as e:
            self.log_test("Error Message Display", False, f"Error testing error display: {e}")
            return False
            
    def close_product_modal(self):
        """Close the product modal"""
        try:
            close_button = self.driver.find_element(
                By.XPATH, 
                "//button[contains(@class, 'close') or contains(@class, 'times')]"
            )
            self.driver.execute_script("arguments[0].click();", close_button)
            
            # Wait for modal to disappear
            WebDriverWait(self.driver, 10).until_not(
                EC.presence_of_element_located((By.CLASS_NAME, "product-modal"))
            )
            
            self.log_test("Product Modal Close", True, "Successfully closed product modal")
            return True
        except Exception as e:
            self.log_test("Product Modal Close", False, f"Failed to close modal: {e}")
            return False
            
    def test_multiple_products(self):
        """Test multiple products for review functionality"""
        print("\n🔄 Testing Multiple Products...")
        
        product_cards = self.find_product_cards()
        if not product_cards:
            return False
            
        success_count = 0
        max_products = min(3, len(product_cards))  # Test up to 3 products
        
        for i in range(max_products):
            print(f"\n📝 Testing Product {i+1}...")
            
            # Open modal for this product
            if self.open_product_modal(product_cards[i]):
                # Check review form
                if self.check_review_form_visibility():
                    success_count += 1
                    
                # Close modal
                self.close_product_modal()
                
                # Wait a bit before next product
                time.sleep(1)
                
        self.log_test("Multiple Products Test", success_count == max_products, 
                     f"{success_count}/{max_products} products passed")
        return success_count == max_products
        
    def run_all_tests(self):
        """Run all frontend tests"""
        print("🚀 Starting TASTY FINGERS Frontend Review Tests")
        print("=" * 60)
        
        # Setup driver
        if not self.setup_driver():
            return False
            
        try:
            # Navigate to site
            if not self.navigate_to_site():
                return False
                
            # Test basic functionality
            product_cards = self.find_product_cards()
            if not product_cards:
                print("❌ No products found to test")
                return False
                
            # Test first product
            if self.open_product_modal(product_cards[0]):
                self.check_review_form_visibility()
                self.test_duplicate_review_ui()
                self.test_error_message_display()
                self.close_product_modal()
                
            # Test multiple products
            self.test_multiple_products()
            
            # Print summary
            print("\n" + "=" * 60)
            print("📊 FRONTEND TEST SUMMARY")
            print("=" * 60)
            
            passed = sum(1 for result in self.test_results if result['success'])
            total = len(self.test_results)
            
            print(f"Total Tests: {total}")
            print(f"Passed: {passed}")
            print(f"Failed: {total - passed}")
            print(f"Success Rate: {(passed/total)*100:.1f}%")
            
            if passed == total:
                print("\n🎉 ALL FRONTEND TESTS PASSED!")
            else:
                print(f"\n⚠️  {total - passed} FRONTEND TESTS FAILED.")
                
            # Print failed tests
            failed_tests = [result for result in self.test_results if not result['success']]
            if failed_tests:
                print("\n❌ Failed Frontend Tests:")
                for test in failed_tests:
                    print(f"  - {test['test']}: {test['message']}")
                    
            return passed == total
            
        finally:
            if self.driver:
                self.driver.quit()

def main():
    """Main function"""
    print("🧪 TASTY FINGERS Frontend Review Test Suite")
    print("This script tests the frontend UI behavior for duplicate reviews")
    print()
    
    # Check if server is running
    try:
        import requests
        response = requests.get("http://127.0.0.1:8000/", timeout=5)
        if response.status_code != 200:
            print("❌ Server is running but main page is not accessible")
            return False
    except ImportError:
        print("⚠️  requests library not available, skipping server check")
    except Exception:
        print("❌ Cannot connect to server. Please make sure the Django server is running on http://127.0.0.1:8000")
        print("   Run: cd backend && python manage.py runserver")
        return False
        
    # Run tests
    tester = FrontendReviewTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ Frontend review system is working correctly!")
        print("   - Product modals open properly")
        print("   - Review forms are visible")
        print("   - Duplicate review UI is handled correctly")
        print("   - Error messages are displayed properly")
    else:
        print("\n❌ Frontend review system has issues that need to be fixed")
        
    return success

if __name__ == "__main__":
    main()
