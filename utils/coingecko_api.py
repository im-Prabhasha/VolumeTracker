import requests
from typing import List, Dict, Optional, Any
import time
from datetime import datetime, timedelta

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

    def _safe_float(self, value: Any, default: float = 0.0) -> float:
        """Safely convert value to float with fallback to default"""
        if value is None:
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default

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
            'price_change_percentage': '24h,1h',  # Get both 24h and 1h price changes
        }

        data = self._make_request('coins/markets', params)
        if not data:
            return []

        # Process and normalize the data
        processed_data = []
        for entry in data:
            try:
                # Safely get numeric values with defaults
                current_volume = self._safe_float(entry.get('total_volume'))
                market_cap = self._safe_float(entry.get('market_cap'))
                current_price = self._safe_float(entry.get('current_price'))
                price_change_1h = self._safe_float(entry.get('price_change_percentage_1h_in_currency'))
                price_change_24h = self._safe_float(entry.get('price_change_percentage_24h'))

                # Calculate volume changes
                volume_change_5min = price_change_1h / 12.0  # Rough estimate
                volume_change_1h = price_change_1h * 1.5  # Estimate using price movement

                # Calculate 24h volume change
                if current_price > 0 and price_change_24h != 0:
                    price_24h_ago = current_price / (1 + price_change_24h / 100)
                    volume_24h_ago = current_volume * price_24h_ago / current_price
                    volume_change_24h = ((current_volume - volume_24h_ago) / volume_24h_ago * 100) if volume_24h_ago > 0 else 0
                else:
                    volume_change_24h = 0

                # Update entry with calculated fields
                processed_entry = {
                    'id': entry.get('id', ''),
                    'name': entry.get('name', ''),
                    'symbol': entry.get('symbol', '').upper(),
                    'current_price': current_price,
                    'market_cap': market_cap,
                    'total_volume': current_volume,
                    'price_change_percentage_24h': price_change_24h,
                    'volume_change_percentage_5m': volume_change_5min,
                    'volume_change_percentage_1h': volume_change_1h,
                    'volume_change_percentage_24h': volume_change_24h
                }
                processed_data.append(processed_entry)

            except Exception as e:
                print(f"Error processing entry: {str(e)}")
                continue

        return processed_data
