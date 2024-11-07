from src.database.db import init_db, Session
from src.database.models import User, Crop, UserRole
from datetime import datetime
import os

def create_initial_data(session):
    """Create initial data for testing"""
    
    # Create initial crops
    crops = [
        Crop(
            name='corn',
            current_price=2.5,
            last_updated=datetime.now()
        ),
        Crop(
            name='wheat',
            current_price=3.0,
            last_updated=datetime.now()
        ),
        Crop(
            name='rice',
            current_price=4.0,
            last_updated=datetime.now()
        ),
        Crop(
            name='soybeans',
            current_price=5.0,
            last_updated=datetime.now()
        ),
        Crop(
            name='coffee',
            current_price=10.0,
            last_updated=datetime.now()
        )
    ]
    
    # Check if crops already exist
    existing_crops = session.query(Crop).all()
    if not existing_crops:
        session.add_all(crops)
        session.commit()
        print("✅ Initial crop data created!")
    else:
        print("ℹ️ Crops already exist in database")

if __name__ == "__main__":
    print("🚀 Initializing database...")
    
    # Create tables
    init_db()
    print("✅ Database tables created!")
    
    # Create initial data
    session = Session()
    try:
        create_initial_data(session)
    finally:
        session.close() 