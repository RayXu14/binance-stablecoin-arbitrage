from binance.spot import Spot
from binance_api_ks import key, secret
import time
import logging
from typing import Dict
from config import parse_args
from logger import setup_logging
from trading_pair import TradingPair
from account import Account
import os
import csv
from datetime import datetime

class SpotOrderTracker:
    def __init__(self, client: Spot, pair, args, record_filename):
        self.client = client
        self.pair = pair
        self.initial_quote = args.initial_quote
        self.initial_base = args.initial_base
        self.available_quote = args.initial_quote
        self.available_base = args.initial_base
        # Track order IDs and their locked amounts
        self.buy_orders: Dict[int, float] = {}   # order_id -> locked quote amount (e.g. USDT)
        self.sell_orders: Dict[int, float] = {}  # order_id -> locked base amount (e.g. USDC)
        
        # Initialize records directory and file
        self.records_dir = args.records_dir
        os.makedirs(self.records_dir, exist_ok=True)
        
        # Use the same file name format as logger.py but with .csv extension
        self.record_file = record_filename.split('.')[0] + '.csv'
        
        # Initialize CSV file with headers
        with open(self.record_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'quoteAsset', 'quoteAmount', 'baseAsset', 'baseAmount', 'totalAmount'])
        
        # Record initial state
        self._record_assets()

    def _record_assets(self):
        """Record current assets to CSV file if total has changed"""
        # Calculate total quote amount (including locked in orders)
        total_quote = self.available_quote + sum(self.buy_orders.values())
        total_base = self.available_base + sum(self.sell_orders.values())

        # Only record if this is the first record or if the total has changed
        if not hasattr(self, '_last_total') or abs(total_quote + total_base - self._last_total) > 1e-8:
            with open(self.record_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().isoformat(),
                    self.pair.quoteAsset,
                    total_quote,
                    self.pair.baseAsset,
                    total_base,
                    total_quote + total_base
                ])
            self._last_total = total_quote
            logging.info(f"Total assets recorded - Quote: {total_quote} {self.pair.quoteAsset}, Base: {total_base} {self.pair.baseAsset}, Total: {total_quote + total_base}")

    def add_buy_order(self, order_id: int, quote_amount: float):
        # Check if order_id already exists
        if order_id in self.buy_orders or order_id in self.sell_orders:
            raise ValueError(f"Order ID {order_id} already exists")
            
        self.buy_orders[order_id] = quote_amount
        self.available_quote -= quote_amount
        logging.info(f"Added buy order {order_id}, locked {quote_amount} {self.pair.quoteAsset}, available {self.pair.quoteAsset}: {self.available_quote}")

    def add_sell_order(self, order_id: int, base_amount: float):
        # Check if order_id already exists
        if order_id in self.buy_orders or order_id in self.sell_orders:
            raise ValueError(f"Order ID {order_id} already exists")
            
        self.sell_orders[order_id] = base_amount
        self.available_base -= base_amount
        logging.info(f"Added sell order {order_id}, locked {base_amount} {self.pair.baseAsset}, available {self.pair.baseAsset}: {self.available_base}")

    def check_order_status(self, order_id: int) -> Dict:
        return self.client.get_order(symbol=self.pair.symbol, orderId=order_id)

    def update_orders(self):
        # Check buy orders
        for order_id in list(self.buy_orders.keys()):
            order = self.check_order_status(order_id)
            locked_quote = self.buy_orders[order_id]
            
            if order['status'] == 'FILLED':
                # qty is base asset amount, price is quote per base
                filled_base = sum(float(fill['qty']) for fill in order['fills'])
                assert filled_base == order['origQty'] == order['executedQty']
                used_quote = sum(float(fill['qty']) * float(fill['price']) for fill in order['fills'])
                self.available_base += filled_base
                # Return any excess quote if filled at better price
                if used_quote < locked_quote:
                    returned_quote = locked_quote - used_quote
                    self.available_quote += returned_quote
                    logging.info(f"Buy order {order_id} saved {returned_quote} {self.pair.quoteAsset} by filling at better price")
                del self.buy_orders[order_id]
                logging.info(f"Buy order {order_id} filled: +{filled_base} {self.pair.baseAsset} (used {used_quote}/{locked_quote} {self.pair.quoteAsset}), avg price: {used_quote/filled_base}")
            else:
                # If there were partial fills, add the filled base asset
                if 'fills' in order:
                    partial_filled_base = sum(float(fill['qty']) for fill in order['fills'])
                    assert partial_filled_base > 0
                    assert partial_filled_base == order['executedQty']
                    assert order['origQty'] > partial_filled_base
                    self.available_base += partial_filled_base
                else:
                    assert order['executedQty'] == 0

                if order['status'] in ['CANCELED', 'EXPIRED', 'TRADE_PREVENTION']:
                    # Return locked quote for canceled orders
                    if 'fills' in order:
                        filled_quote = sum(float(fill['qty']) * float(fill['price']) for fill in order.get('fills', []))
                        returned_quote = locked_quote - filled_quote
                    else:
                        returned_quote = locked_quote
                    self.available_quote += returned_quote
                    del self.buy_orders[order_id]
                    logging.info(f"Buy order {order_id} canceled: returned {returned_quote}/{locked_quote} {self.pair.quoteAsset}")
                else:
                    assert order['status'] == 'TRADE'

        # Check sell orders
        for order_id in list(self.sell_orders.keys()):
            order = self.check_order_status(order_id)
            locked_base = self.sell_orders[order_id]
            
            if order['status'] == 'FILLED':
                # qty is base asset amount, price is quote per base
                sold_base = sum(float(fill['qty']) for fill in order['fills'])
                assert sold_base == order['origQty'] == order['executedQty']
                received_quote = sum(float(fill['qty']) * float(fill['price']) for fill in order['fills'])
                self.available_quote += received_quote
                del self.sell_orders[order_id]
                logging.info(f"Sell order {order_id} filled: -{sold_base}/{locked_base} {self.pair.baseAsset} (received {received_quote} {self.pair.quoteAsset}), avg price: {received_quote/sold_base}")
            else:
                # If there were partial fills, add the received quote asset
                if 'fills' in order:
                    filled_base = sum(float(fill['qty']) for fill in order['fills'])
                    assert filled_base > 0
                    assert filled_base == order['executedQty']
                    assert order['origQty'] > filled_base
                    partial_received_quote = sum(float(fill['qty']) * float(fill['price']) for fill in order['fills'])
                    self.available_quote += partial_received_quote
                else:
                    assert order['executedQty'] == 0

                if order['status'] in ['CANCELED', 'EXPIRED', 'TRADE_PREVENTION']:
                    # Return locked base for canceled orders
                    if 'fills' in order:
                        returned_base = locked_base - filled_base
                    else:
                        returned_base = locked_base
                    self.available_base += returned_base
                    del self.sell_orders[order_id]
                    logging.info(f"Sell order {order_id} canceled: returned {returned_base}/{locked_base} {self.pair.baseAsset}")
                else:
                    assert order['status'] == 'TRADE'

        # Log current trading status
        logging.info(f"Available for trading - {self.pair.quoteAsset}: {self.available_quote}, {self.pair.baseAsset}: {self.available_base}")
        logging.info(f"Pending orders - Buy: {len(self.buy_orders)}, Sell: {len(self.sell_orders)}")
        
        # Record current assets
        self._record_assets()

def main():
    args = parse_args()
    log_filename = setup_logging(args)
    
    client = Spot(api_key=key, api_secret=secret)
    account = Account(client)
    pair = TradingPair(client, f"{args.base_asset}{args.quote_asset}")
    
    # Verify initial capital against balance
    if not account.verify_balance(pair.quoteAsset, args.initial_quote):
        return
    
    if not account.verify_balance(pair.baseAsset, args.initial_base):
        return

    logging.info(f"Initial capital verification passed:")
    logging.info(f"{pair.quoteAsset}: {args.initial_quote} <= {account.get_free_balance(pair.quoteAsset)}")
    logging.info(f"{pair.baseAsset}: {args.initial_base} <= {account.get_free_balance(pair.baseAsset)}")

    # Initialize order tracker
    tracker = SpotOrderTracker(
        client=client,
        pair=pair,
        args=args,
        record_filename=log_filename
    )

    retry_count = 0
    while retry_count < args.max_retry:
        try:
            # First update order status and balances
            tracker.update_orders()
            
            # Calculate maximum quantity we can buy with available quote asset
            raw_quantity = tracker.available_quote / args.buy_price
            quantity = pair.round_qty(raw_quantity)
            quote_to_use = quantity * args.buy_price
            if quantity >= pair.min_qty and quote_to_use >= pair.min_notional:
                logging.info(f"Placing buy order - Quantity: {quantity} {pair.baseAsset} at price: {args.buy_price} {pair.quoteAsset}")
                order = client.new_order(
                    symbol=pair.symbol,
                    side='BUY',
                    type='LIMIT',
                    timeInForce='GTC',  # Good-Till-Cancel
                    quantity=quantity,
                    price=args.buy_price
                )
                tracker.add_buy_order(int(order['orderId']), quote_to_use)

            # First update order status and balances
            tracker.update_orders()
            
            # Calculate sell price by adding spread to buy price
            sell_price = args.buy_price + args.price_spread

            # Place sell order if we have available base asset
            quantity = pair.round_qty(tracker.available_base)
            if quantity >= pair.min_qty and quantity * sell_price >= pair.min_notional:
                logging.info(f"Placing sell order - Quantity: {quantity} {pair.baseAsset} at price: {sell_price} {pair.quoteAsset}")
                order = client.new_order(
                    symbol=pair.symbol,
                    side='SELL',
                    type='LIMIT',
                    timeInForce='GTC',
                    quantity=quantity,
                    price=sell_price
                )
                tracker.add_sell_order(int(order['orderId']), quantity)

            # Reset retry count on successful iteration
            retry_count = 0
            time.sleep(args.check_interval)  # Wait before next iteration

        except ValueError as e:
            logging.error(f"ValueError occurred: {e}", exc_info=True)
            break
        
        except Exception as e:
            retry_count += 1
            logging.error(f"An error occurred (attempt {retry_count}/{args.max_retry}): {e}", exc_info=True)
            if retry_count >= args.max_retry:
                logging.error("Maximum retry attempts reached. Exiting...")
                break
            time.sleep(args.retry_interval)  # Wait before retrying

if __name__ == "__main__":
    main()
