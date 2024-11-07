import requests
import logging
from datetime import datetime
from typing import Optional, Dict
import os
import random
from time import time
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class PriceOracle:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        self.base_url = "https://www.alphavantage.co/query"
        
        # Mapping crop names to Alpha Vantage symbols
        self.crop_symbols = {
            'corn': 'CORN',
            'wheat': 'WHEAT',
            'soybeans': 'SOYBEAN',
            'coffee': 'COFFEE',
            'rice': 'RICE'
        }
        
        # Base prices for fallback/simulation
        self.base_prices = {
            'corn': 2.5,
            'wheat': 3.0,
            'soybeans': 5.0,
            'coffee': 10.0,
            'rice': 4.0
        }
        
        # Cache prices to avoid hitting API limits
        self.price_cache = {}
        self.cache_duration = 300  # 5 minutes cache
        
    def get_crop_price(self, crop_name: str) -> Optional[float]:
        """Get current price for a crop from Alpha Vantage with fallback to simulation"""
        try:
            crop_name = crop_name.lower()
            if crop_name not in self.crop_symbols:
                logger.error(f"Unsupported crop: {crop_name}")
                return None
                
            # Check cache first
            if self._is_cache_valid(crop_name):
                logger.info(f"Using cached price for {crop_name}")
                return self.price_cache[crop_name]['price']
                
            # Try to get real price from Alpha Vantage
            real_price = self._get_alpha_vantage_price(crop_name)
            if real_price:
                logger.info(f"Got real price from Alpha Vantage for {crop_name}: {real_price}")
                self._update_cache(crop_name, real_price)
                return real_price
                
            # Fallback to simulated price
            logger.info(f"Using simulated price for {crop_name}")
            simulated_price = self._get_simulated_price(crop_name)
            self._update_cache(crop_name, simulated_price)
            return simulated_price
            
        except Exception as e:
            logger.error(f"Error getting price for {crop_name}: {str(e)}")
            return self.base_prices.get(crop_name)
            
    def _get_alpha_vantage_price(self, crop_name: str) -> Optional[float]:
        """Get real-time price from Alpha Vantage API"""
        try:
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': self.crop_symbols[crop_name],
                'apikey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'Global Quote' in data and '05. price' in data['Global Quote']:
                price = float(data['Global Quote']['05. price'])
                return round(price, 2)
                
            return None
            
        except Exception as e:
            logger.error(f"Alpha Vantage API error: {str(e)}")
            return None
            
    def _get_simulated_price(self, crop_name: str) -> float:
        """Generate simulated price with random variation"""
        base_price = self.base_prices[crop_name]
        volatility = 0.05  # 5% volatility
        trend = 0.001  # 0.1% upward trend per minute
        
        # Calculate time-based trend
        current_time = time()
        minutes_elapsed = (current_time - self.last_update) / 60 if hasattr(self, 'last_update') else 0
        trend_factor = 1 + (trend * minutes_elapsed)
        
        # Add random walk component
        random_factor = 1 + random.uniform(-volatility, volatility)
        
        # Calculate new price
        new_price = base_price * trend_factor * random_factor
        self.last_update = current_time
        
        return round(new_price, 2)
            
    def _update_cache(self, crop_name: str, price: float):
        """Update price cache"""
        self.price_cache[crop_name] = {
            'price': price,
            'timestamp': datetime.now()
        }
            
    def _is_cache_valid(self, crop_name: str) -> bool:
        """Check if cached price is still valid"""
        if crop_name not in self.price_cache:
            return False
            
        cache_age = (datetime.now() - self.price_cache[crop_name]['timestamp']).total_seconds()
        return cache_age < self.cache_duration