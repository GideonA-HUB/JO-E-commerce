import requests
from django.conf import settings
from django.http import JsonResponse
import json

class PaystackService:
    """Service class for handling Paystack payment operations"""
    
    def __init__(self):
        self.secret_key = settings.PAYSTACK_SECRET_KEY
        self.public_key = settings.PAYSTACK_PUBLIC_KEY
        self.base_url = "https://api.paystack.co"
    
    def initialize_transaction(self, order_data):
        """Initialize a Paystack transaction"""
        try:
            url = f"{self.base_url}/transaction/initialize"
            headers = {
                "Authorization": f"Bearer {self.secret_key}",
                "Content-Type": "application/json"
            }
            
            # Prepare transaction data
            payload = {
                "email": order_data['email'],
                "amount": int(float(order_data['total_amount']) * 100),  # Convert to kobo
                "currency": "NGN",
                "reference": f"TASTY_FINGERS_{order_data.get('order_id', 'ORDER')}",
                "callback_url": f"{settings.SITE_URL}/api/paystack/verify/",
                "metadata": {
                    "order_id": order_data.get('order_id'),
                    "customer_name": f"{order_data['first_name']} {order_data['last_name']}",
                    "customer_phone": order_data.get('phone', ''),
                    "delivery_address": order_data.get('address', ''),
                    "items": order_data.get('items', [])
                }
            }
            
            response = requests.post(url, headers=headers, json=payload)
            response_data = response.json()
            
            if response.status_code == 200 and response_data['status']:
                return {
                    'success': True,
                    'authorization_url': response_data['data']['authorization_url'],
                    'reference': response_data['data']['reference'],
                    'access_code': response_data['data']['access_code']
                }
            else:
                return {
                    'success': False,
                    'error': response_data.get('message', 'Failed to initialize transaction')
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Network error: {str(e)}'
            }
    
    def verify_transaction(self, reference):
        """Verify a Paystack transaction"""
        try:
            url = f"{self.base_url}/transaction/verify/{reference}"
            headers = {
                "Authorization": f"Bearer {self.secret_key}"
            }
            
            response = requests.get(url, headers=headers)
            response_data = response.json()
            
            if response.status_code == 200 and response_data['status']:
                transaction_data = response_data['data']
                return {
                    'success': True,
                    'transaction_id': transaction_data['id'],
                    'reference': transaction_data['reference'],
                    'amount': transaction_data['amount'] / 100,  # Convert from kobo to naira
                    'status': transaction_data['status'],
                    'gateway_response': transaction_data['gateway_response'],
                    'paid_at': transaction_data.get('paid_at'),
                    'metadata': transaction_data.get('metadata', {})
                }
            else:
                return {
                    'success': False,
                    'error': response_data.get('message', 'Failed to verify transaction')
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Network error: {str(e)}'
            }
    
    def create_transfer_recipient(self, bank_data):
        """Create a transfer recipient for payouts"""
        try:
            url = f"{self.base_url}/transferrecipient"
            headers = {
                "Authorization": f"Bearer {self.secret_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "type": "nuban",
                "name": bank_data['account_name'],
                "account_number": bank_data['account_number'],
                "bank_code": bank_data['bank_code'],
                "currency": "NGN"
            }
            
            response = requests.post(url, headers=headers, json=payload)
            response_data = response.json()
            
            if response.status_code == 200 and response_data['status']:
                return {
                    'success': True,
                    'recipient_code': response_data['data']['recipient_code']
                }
            else:
                return {
                    'success': False,
                    'error': response_data.get('message', 'Failed to create recipient')
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Network error: {str(e)}'
            }
    
    def initiate_transfer(self, recipient_code, amount, reason):
        """Initiate a transfer to a recipient"""
        try:
            url = f"{self.base_url}/transfer"
            headers = {
                "Authorization": f"Bearer {self.secret_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "source": "balance",
                "amount": int(amount * 100),  # Convert to kobo
                "recipient": recipient_code,
                "reason": reason,
                "currency": "NGN"
            }
            
            response = requests.post(url, headers=headers, json=payload)
            response_data = response.json()
            
            if response.status_code == 200 and response_data['status']:
                return {
                    'success': True,
                    'transfer_code': response_data['data']['transfer_code'],
                    'reference': response_data['data']['reference']
                }
            else:
                return {
                    'success': False,
                    'error': response_data.get('message', 'Failed to initiate transfer')
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Network error: {str(e)}'
            } 