#!/usr/bin/env python
import click
import uvicorn
from src.database.db import init_db, Session
from src.database.models import Crop, User, UserRole, Future
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

@cli.command()
@click.argument('phone', required=False)
def list_futures(phone):
    """List all futures contracts or filter by phone number"""
    try:
        session = Session()
        query = session.query(Future).join(User)
        
        if phone:
            query = query.filter(User.phone_number == phone)
            
        futures = query.all()
        
        if not futures:
            click.echo("No futures contracts found.")
            return
            
        click.echo("\n🌾 Futures Contracts")
        click.echo("=" * 80)
        click.echo(f"{'ID':4} {'Farmer':15} {'Crop':10} {'Quantity':10} {'Strike':8} {'Premium':8} {'Status':10} {'Created'}")
        click.echo("-" * 80)
        
        for future in futures:
            click.echo(
                f"{future.id:<4} "
                f"{future.user.name[:15]:<15} "
                f"{future.crop.name:<10} "
                f"{future.quantity:<10.2f} "
                f"{future.strike_price:<8.2f} "
                f"{future.premium:<8.2f} "
                f"{future.status:<10} "
                f"{future.created_at.strftime('%Y-%m-%d')}"
            )
            
        click.echo("-" * 80)
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}")
    finally:
        session.close()

@cli.command()
@click.argument('future_id', type=int)
def show_future(future_id):
    """Show detailed information about a specific future contract"""
    try:
        session = Session()
        future = session.query(Future).filter_by(id=future_id).first()
        
        if not future:
            click.echo(f"No future contract found with ID {future_id}")
            return
            
        click.echo("\n🔎 Future Contract Details")
        click.echo("=" * 50)
        click.echo(f"ID:            {future.id}")
        click.echo(f"Farmer:        {future.user.name}")
        click.echo(f"Phone:         {future.user.phone_number}")
        click.echo(f"Crop:          {future.crop.name}")
        click.echo(f"Quantity:      {future.quantity} kg")
        click.echo(f"Strike Price:  {future.strike_price} KES/kg")
        click.echo(f"Premium:       {future.premium} KES")
        click.echo(f"Status:        {future.status}")
        click.echo(f"Created:       {future.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        click.echo(f"Expires:       {future.expiration_date.strftime('%Y-%m-%d %H:%M:%S')}")
        click.echo(f"Contract ID:   {future.contract_address}")
        
        # Get current price
        crop = session.query(Crop).filter_by(id=future.crop_id).first()
        click.echo(f"Current Price: {crop.current_price} KES/kg")
        
        # Calculate potential payout
        if crop.current_price < future.strike_price:
            payout = (future.strike_price - crop.current_price) * future.quantity
            click.echo(f"Potential Payout: {payout} KES")
        
        click.echo("=" * 50)
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}")
    finally:
        session.close()

if __name__ == '__main__':
    cli() 