from fastapi import FastAPI, HTTPException, Depends, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
import logging

from src.database.db import get_session
from src.database.models import User, Crop, Future, Transaction
from src.blockchain.stellar import StellarBlockchain
from src.payments.rapyd import RapydClient
from src.sms.handler import SMSHandler
from src.sms.messaging import SMSMessenger

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AgriFutures API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependencies
def get_db():
    """Dependency for database session"""
    db = get_session()
    try:
        yield db
    finally:
        db.close()

def get_stellar():
    return StellarBlockchain()

def get_rapyd():
    return RapydClient()

def get_sms():
    return SMSMessenger()

# Routes
@app.post("/webhook/sms")
async def handle_sms(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle incoming SMS messages from Twilio"""
    try:
        # Get form data from request
        form_data = await request.form()
        
        # Log incoming message details
        logger.info(f"Received SMS - From: {form_data.get('From')} Body: {form_data.get('Body')}")
        
        # Process message
        handler = SMSHandler(db)
        response = handler.process_message(
            from_number=form_data.get('From', ''),
            message=form_data.get('Body', '')
        )
        
        # Send response
        if response:
            sms = get_sms()
            success = sms.send_sms(form_data.get('From'), response)
            if not success:
                logger.error("Failed to send SMS response")
        
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Error processing SMS: {str(e)}")
        return {"status": "error", "message": str(e)}

@app.get("/crops")
async def get_crops(db: Session = Depends(get_db)) -> List[dict]:
    """Get list of available crops and current prices"""
    crops = db.query(Crop).all()
    return [
        {
            "id": crop.id,
            "name": crop.name,
            "current_price": crop.current_price,
            "last_updated": crop.last_updated
        }
        for crop in crops
    ]

@app.get("/users/{phone_number}/futures")
async def get_user_futures(
    phone_number: str,
    db: Session = Depends(get_db)
) -> List[dict]:
    """Get user's active futures contracts"""
    user = db.query(User).filter_by(phone_number=phone_number).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    futures = db.query(Future).filter_by(user_id=user.id, status='active').all()
    return [
        {
            "id": future.id,
            "crop": future.crop.name,
            "quantity": future.quantity,
            "strike_price": future.strike_price,
            "premium": future.premium,
            "expiration_date": future.expiration_date
        }
        for future in futures
    ]

@app.post("/users/{phone_number}/deposit")
async def deposit_funds(
    phone_number: str,
    amount: float,
    currency: str,
    db: Session = Depends(get_db)
):
    """Process deposit to user's wallet"""
    user = db.query(User).filter_by(phone_number=phone_number).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    rapyd = get_rapyd()
    transaction_id = rapyd.deposit_funds(user.wallet.rapyd_wallet_id, amount, currency)
    
    if transaction_id:
        transaction = Transaction(
            wallet_id=user.wallet.id,
            amount=amount,
            transaction_type='deposit',
            status='completed',
            rapyd_transaction_id=transaction_id,
            created_at=datetime.now()
        )
        db.add(transaction)
        db.commit()
        return {"status": "success", "transaction_id": transaction_id}
    
    raise HTTPException(status_code=400, detail="Deposit failed")

@app.post("/webhook/rapyd")
async def handle_rapyd_webhook(
    data: dict,
    db: Session = Depends(get_db)
):
    """Handle Rapyd payment webhooks"""
    # Implement webhook handling for payment status updates
    pass