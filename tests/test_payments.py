import pytest
from src.payments.rapyd import RapydClient
from unittest.mock import patch, MagicMock

@pytest.fixture
def rapyd():
    return RapydClient()

class TestRapydMobileMoneyIntegration:
    def test_create_farmer_wallet(self, rapyd):
        """Test creating a mobile money wallet for a woman farmer"""
        with patch.object(rapyd, '_make_request') as mock_request:
            # Setup - simulate successful wallet creation
            mock_request.return_value = {
                'status': {'status': 'SUCCESS'},
                'data': {'id': 'ewallet_123'}
            }
            
            # Execute - create wallet for farmer with mobile number
            wallet_id = rapyd.create_wallet(
                phone_number='+254700000000',  # Example Kenyan number
                country='KE'
            )
            
            # Assert
            assert wallet_id == 'ewallet_123'
            mock_request.assert_called_once()
            
    def test_add_mpesa_payment_method(self, rapyd):
        """Test adding M-PESA as payment method for Kenyan farmers"""
        with patch.object(rapyd, '_make_request') as mock_request:
            mock_request.return_value = {
                'status': {'status': 'SUCCESS'}
            }
            
            payment_method = {
                'type': 'ke_mpesa',
                'method_type': 'mobile_money',
                'fields': {
                    'phone_number': '+254700000000',
                    'name': 'Jane Farmer'
                }
            }
            
            result = rapyd.add_payment_method('ewallet_123', payment_method)
            assert result is True
            
    def test_process_premium_payment(self, rapyd):
        """Test processing premium payment via mobile money"""
        with patch.object(rapyd, '_make_request') as mock_request:
            mock_request.return_value = {
                'status': {'status': 'SUCCESS'},
                'data': {'id': 'transaction_123'}
            }
            
            transaction_id = rapyd.deposit_funds(
                wallet_id='ewallet_123',
                amount=500.0,  # 500 KES premium
                currency='KES'
            )
            
            assert transaction_id == 'transaction_123'
            
    def test_process_payout(self, rapyd):
        """Test processing contract payout to farmer's mobile money"""
        with patch.object(rapyd, '_make_request') as mock_request:
            mock_request.return_value = {
                'status': {'status': 'SUCCESS'},
                'data': {'id': 'payout_123'}
            }
            
            result = rapyd.withdraw_funds(
                wallet_id='ewallet_123',
                amount=1000.0,  # 1000 KES payout
                currency='KES'
            )
            
            assert result == 'payout_123' 