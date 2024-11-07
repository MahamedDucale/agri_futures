from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()

class UserRole(enum.Enum):
    FARMER = "farmer"
    ADMIN = "admin"

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    phone_number = Column(String, unique=True, nullable=False)
    stellar_public_key = Column(String, unique=True, nullable=False)
    stellar_private_key = Column(String, unique=True, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.FARMER)
    language_preference = Column(String, default='en')
    created_at = Column(DateTime, nullable=False)
    name = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    location = Column(String, nullable=False)
    farm_size = Column(Float)  # in acres
    primary_crop = Column(Integer, ForeignKey('crops.id'))
    
    # Relationships
    futures = relationship("Future", back_populates="user")
    wallet = relationship("Wallet", back_populates="user", uselist=False)

class Crop(Base):
    __tablename__ = 'crops'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    current_price = Column(Float, nullable=False)
    last_updated = Column(DateTime, nullable=False)

class Future(Base):
    __tablename__ = 'futures'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    crop_id = Column(Integer, ForeignKey('crops.id'))
    quantity = Column(Float, nullable=False)  # in kg
    strike_price = Column(Float, nullable=False)  # price per kg
    premium = Column(Float, nullable=False)
    expiration_date = Column(DateTime, nullable=False)
    contract_address = Column(String, nullable=False)  # Stellar contract identifier
    status = Column(String, nullable=False)  # active, expired, exercised
    created_at = Column(DateTime, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="futures")
    crop = relationship("Crop")

class Wallet(Base):
    __tablename__ = 'wallets'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)
    balance = Column(Float, default=0.0)
    rapyd_wallet_id = Column(String, unique=True, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="wallet")

class Transaction(Base):
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    wallet_id = Column(Integer, ForeignKey('wallets.id'))
    amount = Column(Float, nullable=False)
    transaction_type = Column(String, nullable=False)  # deposit, withdrawal, premium_payment
    status = Column(String, nullable=False)  # pending, completed, failed
    rapyd_transaction_id = Column(String, unique=True)
    created_at = Column(DateTime, nullable=False) 