from twilio.rest import Client
import os
from typing import Dict
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SMSMessenger:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Get Twilio credentials
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.from_number = os.getenv('TWILIO_PHONE_NUMBER')
        
        if not all([account_sid, auth_token, self.from_number]):
            raise ValueError(
                "Missing Twilio credentials. Please check your .env file for "
                "TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER"
            )
            
        logger.info(f"Initializing Twilio client with number: {self.from_number}")
        # Initialize Twilio client
        self.client = Client(account_sid, auth_token)
        
    def send_sms(self, to_number: str, message: str) -> bool:
        """Send SMS message using Twilio"""
        try:
            logger.info(f"Attempting to send SMS to {to_number}")
            message = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number
            )
            logger.info(f"SMS sent successfully. Message SID: {message.sid}")
            return True
        except Exception as e:
            logger.error(f"Failed to send SMS to {to_number}: {str(e)}")
            return False
            
    def get_translated_message(self, message_key: str, language: str, **kwargs) -> str:
        """Get translated message template and fill in variables"""
        messages = {
            'en': {
                'welcome': "Welcome to AgriFutures! Your account has been created.",
                'invalid_command': "Invalid command. Send 'menu' for available commands.",
                'future_created': "Future created: {quantity} kg of {crop} at {strike_price}/kg. Premium paid: {premium}",
                'insufficient_funds': "Insufficient funds in your wallet.",
                # Add more message templates
            },
            'sw': {
                'welcome': "Karibu AgriFutures! Akaunti yako imeundwa.",
                'invalid_command': "Amri si sahihi. Tuma 'menyu' kwa amri zinazopatikana.",
                'future_created': "Mkataba umoundwa: {quantity} kg ya {crop} kwa {strike_price}/kg. Malipo: {premium}",
                'insufficient_funds': "Salio hailitoshi kwenye pochi yako.",
                # Add more Swahili translations
            }
        }
        
        template = messages.get(language, messages['en']).get(message_key, messages['en'][message_key])
        return template.format(**kwargs) 