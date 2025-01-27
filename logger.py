import os
import logging
from datetime import datetime

def setup_logging(args) -> None:
    """Setup logging configuration
    
    Args:
        args: Command line arguments
    """
    # Create logs directory if it doesn't exist
    os.makedirs(args.logs_directory, exist_ok=True)
    
    # Create log filename based on init time and arguments
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_filename = os.path.join(
        args.logs_directory, 
        f"{timestamp}_{args.base_asset}{args.initial_base}_{args.quote_asset}{args.initial_quote}_buy{args.buy_price}_sell{args.sell_price}.log"
    )
    
    # Configure logging to file only
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename)
        ]
    )
    
    # Log all arguments
    logging.info("Command line arguments:")
    args_dict = vars(args)
    for key, value in args_dict.items():
        logging.info(f"  {key}: {value}")

if __name__ == '__main__':
    # Import necessary modules
    from binance.spot import Spot
    from binance_api_ks import key, secret
    from trading_pair import TradingPair
    from config import parse_args
    
    # Parse arguments with default values
    import sys
    sys.argv = [
        sys.argv[0],
        '--base_asset', 'USDC',
        '--quote_asset', 'USDT',
        '--initial_quote', '100',
        '--buy_price', '0.99',
        '--sell_price', '1.01'
    ]
    args = parse_args()
    
    # Setup logging
    setup_logging(args)
    
    # Test logging by getting some real trading pair info
    client = Spot(api_key=key, api_secret=secret)
    pair = TradingPair(client, f"{args.base_asset}{args.quote_asset}")
    
    # Log some test messages
    logging.info("Logger test completed successfully")