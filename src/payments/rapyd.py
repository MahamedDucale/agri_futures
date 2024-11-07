import hashlib
import base64
import json
import requests
import hmac
import os
from datetime import datetime
from typing import Dict, Optional

class RapydClient:
    def __init__(self):
        self.access_key = os.getenv('RAPYD_ACCESS_KEY')
        self.secret_key = os.getenv('RAPYD_SECRET_KEY')
        self.base_url = os.getenv('RAPYD_BASE_URL')

    def _generate_salt(self) -> str:
        return base64.b64encode(os.urandom(16)).decode('ascii')

    def _generate_signature(self, method: str, path: str, salt: str, timestamp: str, body: Dict = None) -> str:
        body_string = json.dumps(body) if body else ''
        to_sign = f"{method.lower()}{path}{salt}{timestamp}{self.access_key}{body_string}"
        
        h = hmac.new(
            self.secret_key.encode('ascii'),
            to_sign.encode('ascii'),
            hashlib.sha256
        )
        
        return base64.b64encode(h.digest()).decode('ascii')

    def _make_request(self, method: str, path: str, body: Dict = None) -> Dict:
        salt = self._generate_salt()
        timestamp = str(int(datetime.now().timestamp()))
        signature = self._generate_signature(method, path, salt, timestamp, body)

        headers = {
            'access_key': self.access_key,
            'salt': salt,
            'timestamp': timestamp,
            'signature': signature,
            'Content-Type': 'application/json'
        }

        url = f"{self.base_url}{path}"
        response = requests.request(
            method,
            url,
            headers=headers,
            json=body if body else None
        )
        
        return response.json()

    def create_wallet(self, phone_number: str, country: str) -> Optional[str]:
        """Create a Rapyd e-wallet for a user"""
        path = '/v1/user'
        body = {
            'phone_number': phone_number,
            'type': 'person',
            'ewallet_reference_id': f'agrifutures_{phone_number}',
            'metadata': {
                'merchant_defined': True
            },
            'country': country,
        }

        response = self._make_request('POST', path, body)
        if response.get('status', {}).get('status') == 'SUCCESS':
            return response['data']['id']
        return None

    def add_payment_method(self, wallet_id: str, payment_method: Dict) -> bool:
        """Add a mobile money payment method to wallet"""
        path = '/v1/payment_methods'
        body = {
            'type': payment_method['type'],
            'ewallet': wallet_id,
            'payment_method_type': payment_method['method_type'],
            'fields': payment_method['fields']
        }

        response = self._make_request('POST', path, body)
        return response.get('status', {}).get('status') == 'SUCCESS'

    def deposit_funds(self, wallet_id: str, amount: float, currency: str) -> Optional[str]:
        """Process a deposit to the wallet"""
        path = '/v1/account/deposit'
        body = {
            'ewallet': wallet_id,
            'amount': amount,
            'currency': currency,
        }

        response = self._make_request('POST', path, body)
        if response.get('status', {}).get('status') == 'SUCCESS':
            return response['data']['id']
        return None

    def withdraw_funds(self, wallet_id: str, amount: float, currency: str) -> Optional[str]:
        """Process a withdrawal from the wallet"""
        path = '/v1/account/withdraw'
        body = {
            'ewallet': wallet_id,
            'amount': amount,
            'currency': currency,
        }

        response = self._make_request('POST', path, body)
        if response.get('status', {}).get('status') == 'SUCCESS':
            return response['data']['id']
        return None

    def get_wallet_balance(self, wallet_id: str) -> Optional[float]:
        """Get current wallet balance"""
        path = f'/v1/user/{wallet_id}'
        response = self._make_request('GET', path)
        
        if response.get('status', {}).get('status') == 'SUCCESS':
            return float(response['data']['accounts'][0]['balance'])
        return None 