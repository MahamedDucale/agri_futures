import pytest
from datetime import datetime, timedelta
from src.blockchain.contracts import FuturesContract
from src.blockchain.stellar import StellarBlockchain
from stellar_sdk import Keypair
from unittest.mock import patch, MagicMock

@pytest.fixture
def contract():
    return FuturesContract()

@pytest.fixture
def stellar():
    return StellarBlockchain()

class TestFuturesContract:
    def test_create_contract_for_farmer(self, contract):
        """Test creating a futures contract for a woman farmer"""
        # Setup
        farmer_keypair = Keypair.random()
        crop_id = 1  # e.g., maize
        quantity = 100.0  # 100 kg
        strike_price = 2.5  # $2.50 per kg
        premium = 5.0  # $5.00 premium
        
        # Execute
        result = contract.create_contract(
            farmer_public_key=farmer_keypair.public_key,
            crop_id=crop_id,
            quantity=quantity,
            strike_price=strike_price,
            premium=premium
        )
        
        # Assert
        assert result["contract_data"]["farmer_key"] == farmer_keypair.public_key
        assert result["contract_data"]["quantity"] == quantity
        assert result["contract_data"]["strike_price"] == strike_price
        assert result["contract_data"]["status"] == "ACTIVE"
        
    def test_contract_exercise_conditions(self, contract):
        """Test when a farmer can exercise their contract"""
        # Setup
        contract_data = {
            "status": "ACTIVE",
            "strike_price": 2.5,
            "quantity": 100,
            "expires_at": (datetime.now() + timedelta(days=30)).isoformat()
        }
        
        # Test cases
        assert contract.is_exercisable(contract_data, current_price=2.0) == True  # Price below strike
        assert contract.is_exercisable(contract_data, current_price=3.0) == False  # Price above strike
        
    def test_payout_calculation(self, contract):
        """Test correct payout calculation for farmers"""
        # Setup
        contract_data = {
            "status": "ACTIVE",
            "strike_price": 2.5,
            "quantity": 100,
            "expires_at": (datetime.now() + timedelta(days=30)).isoformat()
        }
        
        # Calculate payout when price drops
        payout = contract.calculate_payout(contract_data, current_price=2.0)
        expected_payout = (2.5 - 2.0) * 100  # (strike - current) * quantity
        assert payout == expected_payout

class TestStellarBlockchain:
    def test_create_farmer_account(self, stellar):
        """Test creating a Stellar account for a farmer"""
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            
            public_key, secret = stellar.create_account()
            
            assert public_key.startswith('G')
            assert secret.startswith('S')
            
    def test_create_futures_contract_on_chain(self, stellar):
        """Test recording futures contract on Stellar"""
        with patch.object(stellar, 'server') as mock_server:
            # Setup
            farmer_keypair = Keypair.random()
            quantity = 100.0
            strike_price = 2.5
            premium = 5.0
            
            mock_server.load_account.return_value = MagicMock()
            mock_server.fetch_base_fee.return_value = 100
            mock_server.submit_transaction.return_value = {'successful': True}
            
            # Execute
            contract_id = stellar.create_futures_contract(
                farmer_keypair.public_key,
                quantity,
                strike_price,
                premium
            )
            
            # Assert
            assert isinstance(contract_id, str)
            assert contract_id.startswith('FUTURE_')
            assert mock_server.submit_transaction.called 