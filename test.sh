#!/bin/bash
nohup python main.py --base_asset FDUSD --initial_quote 1000 --buy_price 0.9998 &
nohup python main.py --base_asset FDUSD --initial_quote 1000 --buy_price 0.9999 &
nohup python main.py --base_asset FDUSD --initial_quote 1000 --buy_price 1.0000 &
nohup python main.py --base_asset FDUSD --initial_quote 1000 --buy_price 1.0001 &
nohup python main.py --base_asset USDC --initial_quote 1000 --buy_price 0.9998 &
nohup python main.py --base_asset USDC --initial_quote 1000 --buy_price 0.9999 &
nohup python main.py --base_asset USDC --initial_quote 1000 --buy_price 1.0000 &
nohup python main.py --base_asset USDC --initial_quote 1000 --buy_price 1.0001 &
