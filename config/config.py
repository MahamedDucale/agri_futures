import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    # Stellar
    STELLAR_NETWORK = os.getenv('STELLAR_NETWORK', 'TESTNET')
    STELLAR_HORIZON_URL = os.getenv('STELLAR_HORIZON_URL')
    STELLAR_ISSUER_SECRET_KEY = os.getenv('STELLAR_ISSUER_SECRET_KEY')
    STELLAR_ISSUER_PUBLIC_KEY = os.getenv('STELLAR_ISSUER_PUBLIC_KEY')
    
    # Rapyd
    RAPYD_ACCESS_KEY = os.getenv('RAPYD_ACCESS_KEY')
    RAPYD_SECRET_KEY = os.getenv('RAPYD_SECRET_KEY')
    RAPYD_BASE_URL = os.getenv('RAPYD_BASE_URL')
    
    # Twilio
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
    
    # Application
    SECRET_KEY = os.getenv('SECRET_KEY')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')
    
    # Futures Configuration
    FUTURES_EXPIRY_DAYS = 90
    MIN_CONTRACT_SIZE = 50  # minimum kg per contract
    MAX_CONTRACT_SIZE = 1000  # maximum kg per contract
    
    # Supported Crops
    SUPPORTED_CROPS = [
        'corn',
        'wheat',
        'rice',
        'soybeans',
        'coffee'
    ]
    
    # Supported Languages
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'sw': 'Swahili',
        'fr': 'French',  # For West Africa
        'pt': 'Portuguese',  # For Mozambique
        'am': 'Amharic',  # For Ethiopia
        'ha': 'Hausa'  # For Nigeria
    }
    
    # Supported Mobile Money Providers
    MOBILE_MONEY_PROVIDERS: Dict[str, Dict[str, Any]] = {
        'KE': {
            'M-PESA': {
                'type': 'ke_mpesa',
                'currencies': ['KES']
            }
        },
        'GH': {
            'MTN': {
                'type': 'gh_mtn',
                'currencies': ['GHS']
            }
        },
        'TZ': {
            'Vodacom': {
                'type': 'tz_vodacom',
                'currencies': ['TZS']
            }
        }
    }
    
    @classmethod
    def get_mobile_money_providers(cls, country_code: str) -> Dict[str, Dict[str, Any]]:
        """Get supported mobile money providers for a country"""
        return cls.MOBILE_MONEY_PROVIDERS.get(country_code, {}) 