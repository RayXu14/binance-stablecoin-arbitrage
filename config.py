import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='Binance Stablecoin Arbitrage Bot')
    # Trading pair parameters
    parser.add_argument('--base_asset', type=str, required=True, help='Trading asset (e.g. USDC)')
    parser.add_argument('--quote_asset', type=str, default="USDT", help='Quote asset (e.g. USDT)')
    
    # Initial capital parameters
    parser.add_argument('--initial_quote', type=float, required=True, help='Initial quote asset amount')
    parser.add_argument('--initial_base', type=float, default=0, help='Initial base asset amount')
    
    # Trading parameters
    parser.add_argument('--buy_price', type=float, required=True, help='Buy price')
    parser.add_argument('--price_spread', type=float, default=0.0001,
                       help='Price spread added to buy price for selling (default: 0.0001)')
    
    # Operation parameters
    parser.add_argument('--check_interval', type=float, default=1.0, 
                       help='Time interval between checks in seconds (default: 1.0)')
    parser.add_argument('--retry_interval', type=float, default=5.0,
                       help='Time to wait after error before retry in seconds (default: 5.0)')
    parser.add_argument('--max_retry', type=int, default=10,
                       help='Maximum number of retries when error occurs (default: 10)')
    parser.add_argument('--logs_directory', type=str, default="logs",
                       help='Directory for log files (default: "logs")')
    
    return parser.parse_args() 