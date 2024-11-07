from typing import Tuple, Optional
from stellar_sdk import Server, Keypair, TransactionBuilder, Network, Asset
from stellar_sdk.exceptions import NotFoundError
import os
from datetime import datetime
import requests
import hashlib
import logging
from dotenv import load_dotenv
from src.database.models import User
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StellarBlockchain:
    def __init__(self, db_session=None):
        # Explicitly load environment variables
        load_dotenv()
        
        self.network = os.getenv('STELLAR_NETWORK', 'TESTNET')
        self.horizon_url = os.getenv('STELLAR_HORIZON_URL')
        self.issuer_secret = os.getenv('STELLAR_ISSUER_SECRET_KEY')
        self.issuer_public = os.getenv('STELLAR_ISSUER_PUBLIC_KEY')
        
        # Add database session
        self.session = db_session
        
        # Debug logging
        logger.info(f"Network: {self.network}")
        logger.info(f"Horizon URL: {self.horizon_url}")
        logger.info(f"Issuer Public Key: {self.issuer_public}")
        logger.info(f"Issuer Secret Key exists: {bool(self.issuer_secret)}")
        
        # Validate credentials on initialization
        if not all([self.issuer_secret, self.issuer_public]):
            logger.error("Missing Stellar credentials:")
            logger.error(f"Secret Key present: {bool(self.issuer_secret)}")
            logger.error(f"Public Key present: {bool(self.issuer_public)}")
            raise ValueError("Missing Stellar issuer credentials in environment variables")
            
        # Validate the secret key format
        try:
            Keypair.from_secret(self.issuer_secret)
            logger.info("Successfully validated Stellar credentials")
        except Exception as e:
            logger.error(f"Invalid Stellar secret key: {str(e)}")
            raise ValueError(f"Invalid Stellar issuer secret key: {str(e)}")
            
        self.server = Server(horizon_url=self.horizon_url)
        
    def create_account(self) -> Tuple[str, str]:
        """Create a new Stellar account for a user"""
        keypair = Keypair.random()
        
        # Fund the account on testnet
        if self.network == 'TESTNET':
            url = f"https://friendbot.stellar.org?addr={keypair.public_key}"
            response = requests.get(url)
            response.raise_for_status()
            
        return keypair.public_key, keypair.secret
        
    def create_futures_contract(
        self,
        farmer_public_key: str,
        quantity: float,
        strike_price: float,
        premium: float
    ) -> str:
        """Create a futures contract on Stellar blockchain"""
        try:
            logger.info(f"Creating futures contract for farmer: {farmer_public_key}")
            
            # Create shorter asset code (max 12 chars)
            timestamp = datetime.now().strftime('%m%d')
            hash_input = f"{farmer_public_key}{timestamp}"
            hash_suffix = hashlib.md5(hash_input.encode()).hexdigest()[:4]
            asset_code = f"FUT{timestamp}{hash_suffix}"
            logger.info(f"Created asset code: {asset_code}")
            
            # Create the custom asset
            future_asset = Asset(asset_code, self.issuer_public)
            
            # Get farmer's secret key
            farmer = self.session.query(User).filter_by(stellar_public_key=farmer_public_key).first()
            if not farmer:
                raise ValueError("Farmer not found")
            farmer_keypair = Keypair.from_secret(farmer.stellar_private_key)
            logger.info("Got farmer keypair")
            
            # Check if farmer's account exists
            try:
                farmer_account = self.server.load_account(farmer_public_key)
                logger.info("Farmer account exists")
            except:
                # Fund the account if it doesn't exist
                logger.info("Funding farmer account...")
                url = f"https://friendbot.stellar.org?addr={farmer_public_key}"
                response = requests.get(url)
                response.raise_for_status()
                farmer_account = self.server.load_account(farmer_public_key)
                logger.info("Farmer account funded")
            
            # Create trustline transaction
            trust_tx = (
                TransactionBuilder(
                    source_account=farmer_account,
                    network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
                    base_fee=self.server.fetch_base_fee(),
                )
                .append_change_trust_op(
                    asset=future_asset,
                    limit=str(int(quantity))
                )
                .build()
            )
            
            # Sign and submit trustline transaction
            trust_tx.sign(farmer_keypair)
            trust_response = self.server.submit_transaction(trust_tx)
            logger.info(f"Trustline response: {trust_response}")
            
            if not trust_response.get('successful', False):
                raise Exception(f"Failed to establish trustline: {trust_response}")
            logger.info("Trustline established successfully")
            
            # Create payment transaction
            issuer_keypair = Keypair.from_secret(self.issuer_secret)
            issuer_account = self.server.load_account(self.issuer_public)
            
            payment_tx = (
                TransactionBuilder(
                    source_account=issuer_account,
                    network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
                    base_fee=self.server.fetch_base_fee(),
                )
                .append_payment_op(
                    destination=farmer_public_key,
                    asset=future_asset,
                    amount=str(int(quantity))
                )
                .build()
            )
            
            # Sign and submit payment transaction
            payment_tx.sign(issuer_keypair)
            logger.info("Payment transaction signed")
            
            response = self.server.submit_transaction(payment_tx)
            logger.info(f"Payment response: {response}")
            
            if not response.get('successful', False):
                raise Exception(f"Payment failed: {response}")
                
            return asset_code
            
        except Exception as e:
            logger.error(f"Error in create_futures_contract: {str(e)}")
            raise
        
    def exercise_future(
        self,
        contract_id: str,
        farmer_public_key: str,
        quantity: float
    ) -> bool:
        """Exercise a futures contract"""
        try:
            # Implementation of future exercise logic
            # This would involve settling the contract at the strike price
            pass
        except Exception as e:
            logger.error(f"Error in exercise_future: {str(e)}")
            return False
            
        return True