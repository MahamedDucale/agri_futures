from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from stellar_sdk import TransactionBuilder, Asset, Server, Network, Keypair
import json
import os

class FuturesContract:
    """
    Manages futures contracts for crop price protection on Stellar blockchain
    Specifically designed for rural women farmers in the Global South
    """
    
    def __init__(self):
        self.network = os.getenv('STELLAR_NETWORK', 'TESTNET')
        self.horizon_url = os.getenv('STELLAR_HORIZON_URL')
        self.server = Server(horizon_url=self.horizon_url)
        
    def create_contract(
        self,
        farmer_public_key: str,
        crop_id: int,
        quantity: float,
        strike_price: float,
        premium: float,
        expiration_days: int = 90
    ) -> Dict[str, Any]:
        """
        Create a new futures contract for a farmer
        
        Args:
            farmer_public_key: Farmer's Stellar public key
            crop_id: ID of the crop being protected
            quantity: Amount of crop in kg
            strike_price: Guaranteed price per kg
            premium: Cost of the contract
            expiration_days: Number of days until contract expires
        
        Returns:
            Contract data including Stellar transaction details
        """
        expiration_date = datetime.now().replace(
            hour=23, minute=59, second=59
        ) + timedelta(days=expiration_days)
        
        contract_data = {
            "type": "FUTURES_CONTRACT",
            "version": "1.0",
            "farmer_key": farmer_public_key,
            "crop_id": crop_id,
            "quantity": quantity,
            "strike_price": strike_price,
            "premium": premium,
            "created_at": datetime.now().isoformat(),
            "expires_at": expiration_date.isoformat(),
            "status": "ACTIVE"
        }
        
        # Create unique contract ID
        contract_id = f"FUTURE_{datetime.now().strftime('%Y%m%d%H%M%S')}_{crop_id}"
        
        # Store contract data in Stellar transaction memo
        encoded_contract = self.encode_contract(contract_data)
        
        return {
            "contract_id": contract_id,
            "contract_data": contract_data,
            "stellar_data": encoded_contract
        }
    
    def encode_contract(self, contract_data: Dict[str, Any]) -> str:
        """Encode contract data for Stellar transaction memo"""
        return json.dumps(contract_data)
    
    def decode_contract(self, encoded_data: str) -> Dict[str, Any]:
        """Decode contract data from Stellar transaction memo"""
        return json.loads(encoded_data)
    
    def is_exercisable(self, contract_data: Dict[str, Any], current_price: float) -> bool:
        """
        Check if contract can be exercised based on current market price
        
        Args:
            contract_data: The futures contract data
            current_price: Current market price of the crop
            
        Returns:
            True if contract can be exercised profitably
        """
        if contract_data['status'] != 'ACTIVE':
            return False
            
        expiration = datetime.fromisoformat(contract_data['expires_at'])
        if datetime.now() > expiration:
            return False
            
        # Contract is exercisable if market price is below strike price
        return current_price < contract_data['strike_price']
    
    def calculate_payout(
        self,
        contract_data: Dict[str, Any],
        current_price: float
    ) -> Optional[float]:
        """
        Calculate payout amount if contract is exercised
        
        Args:
            contract_data: The futures contract data
            current_price: Current market price of the crop
            
        Returns:
            Payout amount or None if contract cannot be exercised
        """
        if not self.is_exercisable(contract_data, current_price):
            return None
            
        price_difference = contract_data['strike_price'] - current_price
        payout = price_difference * contract_data['quantity']
        
        return max(0, payout) 