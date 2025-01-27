from typing import Dict, Any
from binance.spot import Spot
import logging
import json

class TradingPair:
    def __init__(self, client: Spot, symbol: str):
        """Initialize trading pair
        
        Args:
            client: Binance client
            symbol: Trading pair symbol (e.g. "USDCUSDT")
        """
        exchange_info = client.exchange_info(symbol=symbol)
        self.symbol_info = exchange_info['symbols'][0]
        
        # Truncate permissionSets for cleaner logging
        if 'permissionSets' in exchange_info['symbols'][0]:
            for permission_set in exchange_info['symbols'][0]['permissionSets']:
                if len(permission_set) > 10:
                    permission_set[10:] = ['...']
        
        # Log raw exchange info
        logging.info(f"Raw exchange info for {symbol}:")
        logging.info(json.dumps(exchange_info, indent=2))
        
        # Log parsed exchange info
        logging.info(f"Parsed exchange info for {symbol}:")
        logging.info(f"  Base asset: {self.baseAsset}, precision: {self.base_precision}")
        logging.info(f"  Quote asset: {self.quoteAsset}, precision: {self.quote_precision}")
        logging.info(f"  Trading constraints:")
        logging.info(f"    Minimum quantity: {self.min_qty} {self.baseAsset}")
        logging.info(f"    Step size: {self.step_size} {self.baseAsset}")
        logging.info(f"    Minimum notional: {self.min_notional} {self.quoteAsset}")
        logging.info(f"    Price precision: {self.price_precision} decimals")
        
    @property
    def symbol(self) -> str:
        return self.symbol_info['symbol']
        
    @property
    def baseAsset(self) -> str:
        return self.symbol_info['baseAsset']
        
    @property
    def quoteAsset(self) -> str:
        return self.symbol_info['quoteAsset']
        
    @property
    def base_precision(self) -> int:
        return self.symbol_info['baseAssetPrecision']
        
    @property
    def quote_precision(self) -> int:
        return self.symbol_info['quoteAssetPrecision']
        
    def _get_filter(self, filter_type: str) -> Dict[str, Any]:
        """Get filter by type
        
        Args:
            filter_type: Filter type to find
            
        Returns:
            Filter configuration
        """
        return next(f for f in self.symbol_info['filters'] if f['filterType'] == filter_type)
        
    @property
    def min_qty(self) -> float:
        """Minimum quantity allowed for orders"""
        return float(self._get_filter('LOT_SIZE')['minQty'])
        
    @property
    def step_size(self) -> float:
        """Minimum quantity increment"""
        return float(self._get_filter('LOT_SIZE')['stepSize'])
        
    @property
    def min_notional(self) -> float:
        """Minimum order value in quote asset"""
        return float(self._get_filter('NOTIONAL')['minNotional'])
        
    @property
    def price_precision(self) -> int:
        """Price decimal precision"""
        tick_size = self._get_filter('PRICE_FILTER')['tickSize']
        return len(tick_size.rstrip('0').split('.')[-1])
        
    def round_qty(self, qty: float) -> float:
        """Round quantity to valid step size
        
        Args:
            qty: Quantity to round
            
        Returns:
            Rounded quantity
        """
        step_size = self.step_size
        return float(int(qty / step_size) * step_size)
        
    def round_price(self, price: float) -> float:
        """Round price to valid tick size
        
        Args:
            price: Price to round
            
        Returns:
            Rounded price
        """
        tick_size = float(self._get_filter('PRICE_FILTER')['tickSize'])
        return float(int(price / tick_size) * tick_size)

if __name__ == '__main__':
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Import API keys
    from binance_api_ks import key, secret
    
    # Test different trading pairs
    client = Spot(api_key=key, api_secret=secret)
    test_pairs = [
        'FDUSDUSDT',
        "USDCUSDT",  # Stablecoin pair
    ]
    
    for symbol in test_pairs:
        logging.info(f"\nTesting {symbol}:")
        
        pair = TradingPair(client, symbol)
        
        # Test quantity rounding
        test_qty = 123.456789
        rounded_qty = pair.round_qty(test_qty)
        logging.info(f"Rounded quantity {test_qty} -> {rounded_qty} {pair.baseAsset}")
        
        # Test price rounding
        test_price = 1234.56789
        rounded_price = pair.round_price(test_price)
        logging.info(f"Rounded price {test_price} -> {rounded_price} {pair.quoteAsset}")
