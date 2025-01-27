from typing import Dict
from binance.spot import Spot
import logging

class Account:
    def __init__(self, client: Spot):
        """Initialize account with Binance client
        
        Args:
            client: Binance client
        """
        self.client = client
        self._refresh()
        
    def _refresh(self) -> None:
        """Refresh account information from Binance"""
        account_info = self.client.account()
        self.account_info = account_info
        self.balances = {
            asset['asset']: {
                'free': float(asset['free']),
                'locked': float(asset['locked'])
            }
            for asset in account_info['balances']
        }
        
        # Log account info
        logging.info("Account information:")
        logging.info(f"  Can trade: {account_info['canTrade']}")
        logging.info(f"  Can withdraw: {account_info['canWithdraw']}")
        logging.info(f"  Can deposit: {account_info['canDeposit']}")
        logging.info("Balances:")
        for asset, balance in self.balances.items():
            if balance['free'] > 0 or balance['locked'] > 0:
                logging.info(f"  {asset}: free={balance['free']}, locked={balance['locked']}")
    
    def get_free_balance(self, asset: str) -> float:
        """Get free balance of an asset
        
        Args:
            asset: Asset symbol (e.g. USDT)
            
        Returns:
            Free balance amount
        """
        return self.balances.get(asset, {'free': 0.0})['free']
    
    def get_locked_balance(self, asset: str) -> float:
        """Get locked balance of an asset
        
        Args:
            asset: Asset symbol (e.g. USDT)
            
        Returns:
            Locked balance amount
        """
        return self.balances.get(asset, {'locked': 0.0})['locked']
    
    def get_total_balance(self, asset: str) -> float:
        """Get total balance of an asset
        
        Args:
            asset: Asset symbol (e.g. USDT)
            
        Returns:
            Total balance amount (free + locked)
        """
        balance = self.balances.get(asset, {'free': 0.0, 'locked': 0.0})
        return balance['free'] + balance['locked']
    
    def verify_balance(self, asset: str, required_amount: float) -> bool:
        """Verify if account has enough free balance of an asset
        
        Args:
            asset: Asset symbol (e.g. USDT)
            required_amount: Required amount
            
        Returns:
            True if account has enough free balance, False otherwise
        """
        free_balance = self.get_free_balance(asset)
        has_enough = free_balance >= required_amount
        if not has_enough:
            logging.error(f"Insufficient {asset} balance: required={required_amount}, available={free_balance}")
        return has_enough

if __name__ == '__main__':
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    
    # Import necessary modules
    from binance_api_ks import key, secret
    
    # Initialize client and account
    client = Spot(api_key=key, api_secret=secret)
    account = Account(client)
    
    # Test balance checks
    test_assets = ['USDT', 'USDC']
    for asset in test_assets:
        free = account.get_free_balance(asset)
        locked = account.get_locked_balance(asset)
        total = account.get_total_balance(asset)
        if total > 0:
            logging.info(f"{asset} balances:")
            logging.info(f"  Free: {free}")
            logging.info(f"  Locked: {locked}")
            logging.info(f"  Total: {total}")
            
            # Test balance verification
            test_amount = free * 1.5
            has_enough = account.verify_balance(asset, test_amount)
            logging.info(f"  Has enough for {test_amount}? {has_enough}") 