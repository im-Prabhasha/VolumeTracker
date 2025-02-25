import requests
from typing import List, Dict, Optional
import time

class CoinGeckoAPI:
    """CoinGecko API client for fetching cryptocurrency market data"""
    
    BASE_URL = "https://api.coingecko.com/api/v3"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'User-Agent': 'Crypto Volume Analysis Tool'
        })

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make a request to the CoinGecko API with rate limiting"""
        try:
            url = f"{self.BASE_URL}/{endpoint}"
            response = self.session.get(url, params=params, timeout=10)
            
            # Handle rate limiting
            if response.status_code == 429:
                time.sleep(60)  # Wait for 60 seconds if rate limited
                return self._make_request(endpoint, params)
                
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {str(e)}")
            return None

    def get_market_data(self, page: int = 1, per_page: int = 250) -> List[Dict]:
        """
        Fetch market data for cryptocurrencies
        
        Args:
            page: Page number for pagination
            per_page: Number of results per page (max 250)
            
        Returns:
            List of dictionaries containing market data
        """
        params = {
            'vs_currency': 'usd',
            'order': 'market_cap_desc',
            'per_page': per_page,
            'page': page,
            'sparkline': False,
            'price_change_percentage': '24h'
        }
        
        data = self._make_request('coins/markets', params)
        return data if data else []
