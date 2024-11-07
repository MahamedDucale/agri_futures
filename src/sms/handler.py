from typing import Tuple, Dict, Any
import re
from datetime import datetime, timedelta
from src.database.models import User, Crop, Future, Wallet, UserRole
from src.blockchain.stellar import StellarBlockchain
from src.payments.rapyd import RapydClient
from .messaging import SMSMessenger
import os
from src.oracle.price_oracle import PriceOracle

class SMSHandler:
    def __init__(self, db_session):
        self.session = db_session
        self.stellar = StellarBlockchain(db_session)
        self.rapyd = RapydClient()
        self.messenger = SMSMessenger()
        self.price_oracle = PriceOracle()
        
        # Add message templates
        self.messages = {
            'en': {
                'welcome': "Welcome to AgriFutures! Your account has been created. Send 'menu' to see available commands.",
                'invalid_command': "Invalid command. Send 'menu' to see available commands.",
                'menu': """Available commands:
1. menu - Show available commands
2. price [crop] - Check crop price
3. buy [crop] [kg] [price] - Buy protection
4. sell - Exercise your protection
5. balance - Check your balance""",
                'future_created': "Future created: {quantity} kg of {crop} at {strike_price}/kg. Premium paid: {premium}",
                'insufficient_funds': "Insufficient funds in your wallet.",
                'invalid_crop': "Invalid crop name. Available crops: corn, wheat, rice, soybeans, coffee",
                'invalid_numbers': "Invalid quantity or price. Please enter valid numbers.",
                'invalid_buy_format': "Invalid format. Use: buy [crop] [quantity] [strike_price]",
                'registration_format': "To register, send: register [name] [location] [crop] [farm_size]",
                'price_check': "Current price for {crop}: {price} KES/kg",
                'registration_error': "Sorry, registration failed. Please try again or contact support.",
                'balance_check': "Your current balance is: {balance} KES",
                'balance_error': "Error checking balance. Please try again.",
                'no_wallet': "No wallet found. Please register first.",
                'buy_error': "Sorry, there was an error creating your futures contract. Please try again.",
                'invalid_exercise_format': "Invalid format. Use: sell [future_id]",
                'invalid_future_id': "Invalid future ID. Please provide a valid number.",
                'invalid_future': "No active future contract found with that ID.",
                'cannot_exercise': "Cannot exercise: current price is above strike price.",
                'exercise_success': "Future exercised successfully! Payout: {payout} KES for {quantity} kg of {crop}. Strike price: {strike_price}, Current price: {current_price}",
                'exercise_error': "Error exercising future. Please try again.",
                'no_wallet': "No wallet found. Please contact support.",
            },
            'sw': {
                'welcome': "Karibu AgriFutures! Akaunti yako imeundwa. Tuma 'menyu' kuona amri zinazopatikana.",
                'invalid_command': "Amri si sahihi. Tuma 'menyu' kuona amri zinazopatikana.",
                'menu': """Amri zinazopatikana:
1. menyu - Onesha amri zote
2. bei [mazao] - Angalia bei ya mazao
3. nunua [mazao] [kg] [bei] - Nunua ulinzi
4. uza - Tumia ulinzi wako
5. salio - Angalia salio lako""",
                'future_created': "Mkataba umoundwa: {quantity} kg ya {crop} kwa {strike_price}/kg. Malipo: {premium}",
                'insufficient_funds': "Salio hailitoshi kwenye pochi yako.",
                'invalid_crop': "Jina la mazao si sahihi.",
                'invalid_numbers': "Kiasi au bei si sahihi.",
                'invalid_buy_format': "Muundo si sahihi. Tumia: nunua [mazao] [kiasi] [bei]",
                'registration_format': "Kujisajili, tuma: sajili [jina] [eneo] [mazao] [ukubwa_wa_shamba]",
                'price_check': "Bei ya sasa ya {crop}: {price} KES/kg",
                'registration_error': "Samahani, usajili umeshindwa. Tafadhali jaribu tena au wasiliana na msaada.",
                'balance_check': "Salio lako ni: {balance} KES",
                'balance_error': "Hitilafu katika kuangalia salio. Tafadhali jaribu tena.",
                'no_wallet': "Hakuna pochi. Tafadhali jisajili kwanza.",
                'buy_error': "Samahani, haitaji kujisajili kwanza. Tafadhali jisajili kwanza au wasiliana na msaada.",
                'invalid_exercise_format': "Muundo si sahihi. Tumia: uza [nambari_ya_mkataba]",
                'invalid_future_id': "Nambari ya mkataba si sahihi. Tafadhali weka nambari sahihi.",
                'invalid_future': "Hakuna mkataba hai uliopatikana na hiyo nambari.",
                'cannot_exercise': "Haiwezi kuuzwa: bei ya sasa iko juu ya bei ya mkataba.",
                'exercise_success': "Mkataba umeuzwa kwa mafanikio! Malipo: {payout} KES kwa {quantity} kg ya {crop}. Bei ya sasa: {strike_price}, Bei ya sasa: {current_price}",
                'exercise_error': "Samahani, haitaji kujisajili kwanza. Tafadhali jisajili kwanza au wasiliana na msaada.",
                'no_wallet': "Hakuna pochi. Tafadhali jisajili kwanza.",
            }
        }
        
    def _get_translated_message(self, key: str, language: str, **kwargs) -> str:
        """Get translated message with optional formatting"""
        # Default to English if language not supported
        lang_messages = self.messages.get(language, self.messages['en'])
        # Get message template, fallback to English if key not found
        template = lang_messages.get(key, self.messages['en'].get(key, ''))
        # Format message with provided kwargs if any
        return template.format(**kwargs) if kwargs else template

    def process_message(self, from_number: str, message: str) -> str:
        """Process incoming SMS messages and return response"""
        user = self.session.query(User).filter_by(phone_number=from_number).first()
        
        if not user:
            return self._handle_registration(from_number, message)
            
        command = message.strip().lower().split()
        if not command:
            return self._get_translated_message("invalid_command", user.language_preference)
            
        commands = {
            'menu': self._handle_menu,
            'menyu': self._handle_menu,
            'price': self._handle_price_check,
            'buy': self._handle_buy_future,
            'balance': self._handle_balance_check,
            'sell': self._handle_exercise_future,
            'uza': self._handle_exercise_future,
            'exercise': self._handle_exercise_future
        }
        
        handler = commands.get(command[0])
        if not handler:
            return self._get_translated_message("invalid_command", user.language_preference)
            
        return handler(user, command[1:])
    
    def _handle_menu(self, user: User, args: list) -> str:
        """Return menu message in user's language"""
        return self._get_translated_message("menu", user.language_preference)
    
    def _handle_registration(self, phone_number: str, message: str) -> str:
        """Handle new user registration"""
        try:
            language = self._detect_language(message)
            parts = message.strip().lower().split()
            
            # Check if this is a registration message
            if parts[0] not in ['register', 'sajili']:
                return self._get_translated_message('registration_format', language)
                
            if len(parts) < 5:
                return self._get_translated_message('registration_format', language)
                
            # Create Stellar account first
            public_key, secret_key = self.stellar.create_account()
            
            # Create Rapyd wallet with proper error handling
            try:
                wallet_id = self.rapyd.create_wallet(
                    phone_number=phone_number,
                    country='KE',  # Default to Kenya for now
                    name=parts[1]  # Use the provided name
                )
                if not wallet_id:
                    raise ValueError("Failed to create Rapyd wallet")
            except Exception as e:
                # For testing, use a dummy wallet ID if Rapyd fails
                if os.getenv('DEBUG', 'False').lower() == 'true':
                    wallet_id = f"test_wallet_{phone_number}"
                else:
                    raise ValueError(f"Failed to create Rapyd wallet: {str(e)}")
            
            # Create user
            user = User(
                phone_number=phone_number,
                stellar_public_key=public_key,
                stellar_private_key=secret_key,
                role=UserRole.FARMER,
                language_preference=language,
                created_at=datetime.now(),
                name=parts[1],
                gender='F',  # Default to female as per project requirements
                location=parts[2],
                farm_size=float(parts[4]),
                primary_crop=1  # Default to first crop, update based on parts[3]
            )
            
            # Create wallet with the obtained Rapyd wallet ID
            wallet = Wallet(
                user=user,
                rapyd_wallet_id=wallet_id,
                balance=0.0
            )
            
            # Add both user and wallet to session
            self.session.add(user)
            self.session.add(wallet)
            
            # Commit the transaction
            try:
                self.session.commit()
            except Exception as e:
                self.session.rollback()
                raise ValueError(f"Failed to save user data: {str(e)}")
            
            return self._get_translated_message('welcome', language)
            
        except Exception as e:
            # Log the error and return a user-friendly message
            print(f"Registration error: {str(e)}")
            return self._get_translated_message('registration_error', language)
    
    def _handle_buy_future(self, user: User, args: list) -> str:
        """Handle purchase of futures contract
        Expected format: buy <crop> <quantity> <strike_price>
        Example: buy corn 100 2.5
        """
        print(f"Buy future request - User: {user.phone_number}, Args: {args}")  # Debug log
        
        if len(args) != 3:
            print(f"Invalid number of arguments: {len(args)}")  # Debug log
            return self._get_translated_message("invalid_buy_format", user.language_preference)
            
        crop_name, quantity, strike_price = args
        try:
            quantity = float(quantity)
            strike_price = float(strike_price)
            print(f"Parsed values - Crop: {crop_name}, Quantity: {quantity}, Price: {strike_price}")  # Debug log
        except ValueError:
            print("Failed to parse quantity or strike price")  # Debug log
            return self._get_translated_message("invalid_numbers", user.language_preference)
            
        crop = self.session.query(Crop).filter_by(name=crop_name).first()
        print(f"Found crop: {crop}")  # Debug log
        
        if not crop:
            print(f"Crop not found: {crop_name}")  # Debug log
            return self._get_translated_message("invalid_crop", user.language_preference)
            
        # Calculate premium
        premium = self._calculate_premium(crop.current_price, strike_price, quantity)
        print(f"Calculated premium: {premium}")  # Debug log
        
        # Check wallet and balance
        if not user.wallet:
            print("No wallet found for user")  # Debug log
            return self._get_translated_message("no_wallet", user.language_preference)
            
        print(f"Current wallet balance: {user.wallet.balance}")  # Debug log
        
        # Add initial test balance if in debug mode
        if os.getenv('DEBUG', 'False').lower() == 'true' and user.wallet.balance == 0:
            user.wallet.balance = 1000.0  # Give 1000 KES for testing
            self.session.commit()
            print("Added initial test balance")  # Debug log
        
        if user.wallet.balance < premium:
            print(f"Insufficient funds: {user.wallet.balance} < {premium}")  # Debug log
            return self._get_translated_message("insufficient_funds", user.language_preference)
            
        try:
            # Create Stellar contract
            contract_address = self.stellar.create_futures_contract(
                user.stellar_public_key,
                quantity,
                strike_price,
                premium
            )
            print(f"Created Stellar contract: {contract_address}")  # Debug log
            
            # Create future record
            future = Future(
                user_id=user.id,
                crop_id=crop.id,
                quantity=quantity,
                strike_price=strike_price,
                premium=premium,
                expiration_date=datetime.now() + timedelta(days=90),
                contract_address=contract_address,
                status='active',
                created_at=datetime.now()
            )
            
            # Deduct premium from wallet
            user.wallet.balance -= premium
            
            self.session.add(future)
            self.session.commit()
            print("Future contract created and saved to database")  # Debug log
            
            return self._get_translated_message(
                "future_created",
                user.language_preference,
                quantity=quantity,
                crop=crop_name,
                strike_price=strike_price,
                premium=premium
            )
        except Exception as e:
            print(f"Error creating future: {str(e)}")  # Debug log
            self.session.rollback()
            return self._get_translated_message("buy_error", user.language_preference)

    def _handle_price_check(self, user: User, args: list) -> str:
        """Handle price check request
        Expected format: price <crop>
        Example: price corn
        """
        print(f"Handling price check for args: {args}")
        
        if not args:
            return self._get_translated_message("invalid_crop", user.language_preference)
            
        crop_name = args[0].lower()
        print(f"Looking up crop: {crop_name}")
        
        # Get real-time price from oracle
        current_price = self.price_oracle.get_crop_price(crop_name)
        
        if current_price is None:
            return self._get_translated_message("invalid_crop", user.language_preference)
            
        # Update price in database
        crop = self.session.query(Crop).filter_by(name=crop_name).first()
        if crop:
            crop.current_price = current_price
            crop.last_updated = datetime.now()
            self.session.commit()
            
        response = self._get_translated_message(
            "price_check",
            user.language_preference,
            crop=crop_name,
            price=current_price
        )
        print(f"Sending response: {response}")
        return response

    def _handle_balance_check(self, user: User, args: list) -> str:
        """Handle balance check request"""
        try:
            print(f"Checking balance for user: {user.phone_number}")  # Debug log
            
            if not user.wallet:
                print("No wallet found for user")  # Debug log
                return self._get_translated_message("no_wallet", user.language_preference)
                
            print(f"Current balance: {user.wallet.balance}")  # Debug log
            
            # Add initial test balance if in debug mode
            if os.getenv('DEBUG', 'False').lower() == 'true' and user.wallet.balance == 0:
                user.wallet.balance = 1000.0  # Give 1000 KES for testing
                self.session.commit()
                print("Added initial test balance")  # Debug log
                
            response = self._get_translated_message(
                "balance_check",
                user.language_preference,
                balance=user.wallet.balance
            )
            print(f"Sending response: {response}")  # Debug log
            return response
            
        except Exception as e:
            print(f"Balance check error: {str(e)}")  # Debug log
            return self._get_translated_message("balance_error", user.language_preference)

    def _handle_exercise_future(self, user: User, args: list) -> str:
        """Handle exercise future request
        Expected format: sell [future_id]
        Example: sell 1
        """
        try:
            print(f"Exercise future request - User: {user.phone_number}, Args: {args}")
            
            if not args:
                return self._get_translated_message("invalid_exercise_format", user.language_preference)
                
            try:
                future_id = int(args[0])
            except ValueError:
                return self._get_translated_message("invalid_future_id", user.language_preference)
                
            # Get the future contract
            future = self.session.query(Future).filter_by(
                id=future_id,
                user_id=user.id,
                status='active'
            ).first()
            
            if not future:
                print(f"No active future found with ID: {future_id}")
                return self._get_translated_message("invalid_future", user.language_preference)
                
            # Get current price
            crop = self.session.query(Crop).filter_by(id=future.crop_id).first()
            print(f"Current price for {crop.name}: {crop.current_price}")
            print(f"Strike price: {future.strike_price}")
            
            # Check if future can be exercised (current price must be below strike price)
            if crop.current_price >= future.strike_price:
                print("Cannot exercise: current price above strike price")
                return self._get_translated_message("cannot_exercise", user.language_preference)
                
            # Calculate payout
            payout = (future.strike_price - crop.current_price) * future.quantity
            print(f"Calculated payout: {payout}")
            
            # Update future status
            future.status = 'exercised'
            
            # Add payout to wallet
            if not user.wallet:
                print("No wallet found for user")
                return self._get_translated_message("no_wallet", user.language_preference)
                
            user.wallet.balance += payout
            
            # Save changes
            self.session.commit()
            print("Future exercised successfully")
            
            return self._get_translated_message(
                "exercise_success",
                user.language_preference,
                payout=payout,
                crop=crop.name,
                quantity=future.quantity,
                strike_price=future.strike_price,
                current_price=crop.current_price
            )
            
        except Exception as e:
            print(f"Error exercising future: {str(e)}")
            self.session.rollback()
            return self._get_translated_message("exercise_error", user.language_preference)

    def _calculate_premium(self, current_price: float, strike_price: float, quantity: float) -> float:
        """Calculate premium for futures contract"""
        # Simple premium calculation (can be made more sophisticated)
        base_premium = abs(strike_price - current_price) * quantity * 0.1
        return max(base_premium, 1.0)  # Minimum premium of 1 unit

    def _detect_language(self, message: str) -> str:
        """Detect language from message content"""
        # Simple language detection based on common words
        swahili_words = {'sajili', 'menyu', 'bei', 'nunua', 'uza', 'salio', 'mazao', 'shamba'}
        words = set(message.lower().split())
        
        # If message contains Swahili words, use Swahili
        if words.intersection(swahili_words):
            return 'sw'
        return 'en'