#!/usr/bin/env python
import click
import uvicorn
from src.database.db import init_db, Session
from src.database.models import Crop, User, UserRole
from datetime import datetime
import os
from dotenv import load_dotenv
from stellar_sdk import Keypair
import requests

# Load environment variables
load_dotenv()

@click.group()
def cli():
    """AgriFutures management CLI"""
    pass

@cli.command()
@click.option('--host', default='127.0.0.1', help='Host to bind to')
@click.option('--port', default=8000, help='Port to bind to')
@click.option('--reload', is_flag=True, help='Enable auto-reload')
def runserver(host, port, reload):
    """Run the development server"""
    click.echo(f"Starting server on {host}:{port}")
    uvicorn.run("src.api.routes:app", host=host, port=port, reload=reload)

@cli.command()
def initdb():
    """Initialize the database"""
    click.echo("Initializing database...")
    try:
        init_db()
        click.echo("✅ Database tables created successfully!")
        
        # Create initial data
        session = Session()
        try:
            create_initial_data(session)
            click.echo("✅ Initial data created successfully!")
        finally:
            session.close()
            
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}")

@cli.command()
def create_stellar():
    """Create and fund a Stellar testnet account"""
    click.echo("Creating Stellar account...")
    try:
        # Generate new keypair
        keypair = Keypair.random()
        public_key = keypair.public_key
        secret_key = keypair.secret
        
        # Fund account using friendbot
        click.echo("Funding account on testnet...")
        response = requests.get(f"https://friendbot.stellar.org?addr={public_key}")
        response.raise_for_status()
        
        click.echo("\n✅ Account created successfully!")
        click.echo(f"\nPublic Key: {public_key}")
        click.echo(f"Secret Key: {secret_key}")
        
        # Update .env file
        if click.confirm("\nUpdate .env file with new keys?"):
            update_env_file(public_key, secret_key)
            
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}")

@cli.command()
@click.argument('phone')
def create_user(phone):
    """Create a test user"""
    try:
        session = Session()
        
        # Create Stellar account
        keypair = Keypair.random()
        
        # Fund account on testnet
        response = requests.get(f"https://friendbot.stellar.org?addr={keypair.public_key}")
        response.raise_for_status()
        
        # Create user
        user = User(
            phone_number=phone,
            stellar_public_key=keypair.public_key,
            stellar_private_key=keypair.secret,
            role=UserRole.FARMER,
            language_preference='en',
            created_at=datetime.now(),
            name='Test User',
            gender='F',
            location='Test Location',
            farm_size=2.5,
            primary_crop=1
        )
        
        session.add(user)
        session.commit()
        
        click.echo(f"✅ User created successfully!")
        click.echo(f"Phone: {phone}")
        click.echo(f"Stellar Public Key: {keypair.public_key}")
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}")
    finally:
        session.close()

def create_initial_data(session):
    """Create initial crop data"""
    crops = [
        Crop(name='corn', current_price=2.5, last_updated=datetime.now()),
        Crop(name='wheat', current_price=3.0, last_updated=datetime.now()),
        Crop(name='rice', current_price=4.0, last_updated=datetime.now()),
        Crop(name='soybeans', current_price=5.0, last_updated=datetime.now()),
        Crop(name='coffee', current_price=10.0, last_updated=datetime.now())
    ]
    
    existing = session.query(Crop).first()
    if not existing:
        session.add_all(crops)
        session.commit()

def update_env_file(public_key, secret_key):
    """Update .env file with Stellar keys"""
    env_path = '.env'
    
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            lines = f.readlines()
            
        with open(env_path, 'w') as f:
            for line in lines:
                if line.startswith('STELLAR_ISSUER_PUBLIC_KEY='):
                    f.write(f'STELLAR_ISSUER_PUBLIC_KEY={public_key}\n')
                elif line.startswith('STELLAR_ISSUER_SECRET_KEY='):
                    f.write(f'STELLAR_ISSUER_SECRET_KEY={secret_key}\n')
                else:
                    f.write(line)
        click.echo("✅ .env file updated successfully!")
    else:
        click.echo("❌ .env file not found!")

if __name__ == '__main__':
    cli() 