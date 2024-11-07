from stellar_sdk import Keypair
import requests
from pathlib import Path
import os
from dotenv import load_dotenv

def create_stellar_account():
    """Create a new Stellar account and fund it on testnet"""
    
    # Generate new keypair
    keypair = Keypair.random()
    
    # Get the keys
    secret_key = keypair.secret
    public_key = keypair.public_key
    
    # Fund the account on testnet using Friendbot
    print("Funding account on testnet...")
    friendbot_url = f"https://friendbot.stellar.org?addr={public_key}"
    response = requests.get(friendbot_url)
    
    if response.status_code == 200:
        print("\n✅ Account successfully created and funded on testnet!")
        print(f"\nPublic Key: {public_key}")
        print(f"Secret Key: {secret_key}")
        
        # Update .env file if it exists
        env_path = Path('.env')
        if env_path.exists():
            update_env = input("\nWould you like to update your .env file with these keys? (y/n): ")
            if update_env.lower() == 'y':
                update_env_file(public_key, secret_key)
        else:
            create_env = input("\nWould you like to create a .env file with these keys? (y/n): ")
            if create_env.lower() == 'y':
                create_env_file(public_key, secret_key)
                
        return public_key, secret_key
    else:
        raise Exception("Failed to fund account on testnet")

def update_env_file(public_key, secret_key):
    """Update existing .env file with new Stellar keys"""
    with open('.env', 'r') as file:
        lines = file.readlines()
    
    with open('.env', 'w') as file:
        stellar_updated = False
        for line in lines:
            if line.startswith('STELLAR_ISSUER_PUBLIC_KEY='):
                file.write(f'STELLAR_ISSUER_PUBLIC_KEY={public_key}\n')
                stellar_updated = True
            elif line.startswith('STELLAR_ISSUER_SECRET_KEY='):
                file.write(f'STELLAR_ISSUER_SECRET_KEY={secret_key}\n')
                stellar_updated = True
            else:
                file.write(line)
        
        if not stellar_updated:
            file.write(f'\nSTELLAR_ISSUER_PUBLIC_KEY={public_key}\n')
            file.write(f'STELLAR_ISSUER_SECRET_KEY={secret_key}\n')
    
    print("✅ .env file updated successfully!")

def create_env_file(public_key, secret_key):
    """Create new .env file with Stellar keys"""
    with open('.env.example', 'r') as example_file:
        env_template = example_file.read()
    
    env_content = env_template.replace('your_issuer_public_key', public_key)
    env_content = env_content.replace('your_issuer_secret_key', secret_key)
    
    with open('.env', 'w') as env_file:
        env_file.write(env_content)
    
    print("✅ .env file created successfully!")

if __name__ == "__main__":
    try:
        print("🚀 Creating new Stellar account...")
        create_stellar_account()
        
        print("\n⚠️  IMPORTANT: Save your secret key securely! You cannot recover it if lost.")
        print("\n📝 Next steps:")
        print("1. Make sure your .env file is properly configured")
        print("2. Never share your secret key")
        print("3. Keep a secure backup of your keys")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}") 