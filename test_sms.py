from src.sms.handler import SMSHandler
from src.database.db import get_db_session

def test_sms():
    with get_db_session() as session:
        handler = SMSHandler(session)
        response = handler.process_message(
            from_number='+1234567890',  # Your phone number
            message='help'  # Test command
        )
        print(f"Response: {response}")

if __name__ == "__main__":
    test_sms() 