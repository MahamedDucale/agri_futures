from src.blockchain.stellar import StellarBlockchain
from dotenv import load_dotenv
import os

def test_stellar_credentials():
    # Load environment variables
    load_dotenv()
    
    # Print environment variables
    print("\nEnvironment Variables:")
    print(f"STELLAR_NETWORK: {os.getenv('STELLAR_NETWORK')}")
    print(f"STELLAR_HORIZON_URL: {os.getenv('STELLAR_HORIZON_URL')}")
    print(f"STELLAR_ISSUER_PUBLIC_KEY: {os.getenv('STELLAR_ISSUER_PUBLIC_KEY')}")
    print(f"STELLAR_ISSUER_SECRET_KEY exists: {bool(os.getenv('STELLAR_ISSUER_SECRET_KEY'))}")
    
    try:
        # Try to initialize StellarBlockchain
        stellar = StellarBlockchain()
        print("\n✅ Successfully initialized StellarBlockchain")
        
        # Try to create a test account
        public_key, secret = stellar.create_account()
        print(f"\nTest account created:")
        print(f"Public Key: {public_key}")
        print(f"Secret Key: {secret}")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    test_stellar_credentials() 