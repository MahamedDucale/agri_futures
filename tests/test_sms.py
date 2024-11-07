import pytest
from datetime import datetime
from src.sms.handler import SMSHandler
from src.sms.messaging import SMSMessenger
from src.database.models import User, Crop, Future, UserRole, Wallet
from unittest.mock import patch, MagicMock

@pytest.fixture
def db_session():
    return MagicMock()

@pytest.fixture
def sms_handler(db_session):
    return SMSHandler(db_session)

class TestSMSHandler:
    def test_register_new_farmer(self, sms_handler, db_session):
        """Test registering a new woman farmer via SMS"""
        # Setup
        db_session.query.return_value.filter_by.return_value.first.return_value = None
        
        # Execute - simulate registration SMS
        response = sms_handler.process_message(
            from_number='+254700000000',
            message='register Jane Farmer'
        )
        
        # Assert
        assert isinstance(response, str)
        assert 'welcome' in response.lower()
        
    def test_check_crop_price(self, sms_handler, db_session):
        """Test checking current crop prices via SMS"""
        # Setup mock user and crop
        user = User(
            phone_number='+254700000000',
            language_preference='sw'  # Swahili
        )
        crop = Crop(
            name='mahindi',  # corn in Swahili
            current_price=50.0,
            last_updated=datetime.now()
        )
        
        db_session.query.return_value.filter_by.return_value.first.side_effect = [
            user, crop
        ]
        
        # Execute - simulate price check SMS
        response = sms_handler.process_message(
            from_number='+254700000000',
            message='bei mahindi'  # "price corn" in Swahili
        )
        
        assert 'mahindi' in response.lower()
        assert '50' in response
        
    def test_buy_future_contract(self, sms_handler, db_session):
        """Test purchasing a futures contract via SMS"""
        # Setup mock objects
        user = User(
            phone_number='+254700000000',
            stellar_public_key='G...',
            wallet=Wallet(balance=1000.0)  # Has enough balance for premium
        )
        crop = Crop(
            name='mahindi',
            current_price=45.0
        )
        
        db_session.query.return_value.filter_by.return_value.first.side_effect = [
            user, crop
        ]
        
        # Execute - simulate buy SMS
        response = sms_handler.process_message(
            from_number='+254700000000',
            message='nunua mahindi 100 50'  # "buy corn 100kg at 50" in Swahili
        )
        
        assert 'successful' in response.lower()
        assert '100' in response
        assert '50' in response 