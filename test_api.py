import requests
import json

# Test the API endpoints
base_url = "http://127.0.0.1:8000"

print("Testing API endpoints...")

# Test products endpoint
try:
    response = requests.get(f"{base_url}/api/products/")
    print(f"Products API Status: {response.status_code}")
    if response.status_code == 200:
        products = response.json()
        print(f"Number of products: {len(products)}")
        if products:
            print(f"First product: {products[0]}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error testing products API: {e}")

# Test catering services endpoint
try:
    response = requests.get(f"{base_url}/api/catering-services/")
    print(f"Catering API Status: {response.status_code}")
    if response.status_code == 200:
        services = response.json()
        print(f"Number of catering services: {len(services)}")
        if services:
            print(f"First service: {services[0]}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error testing catering API: {e}")

print("Test completed.") 