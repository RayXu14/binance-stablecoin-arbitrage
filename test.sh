#!/bin/bash
# Recommended to run in a tmux session to avoid interruption (I know it's weird but ...)
# nohup python -u main.py --base_asset FDUSD --initial_quote 1000 --buy_price 0.9998 > logs/1.log 2>&1 &
# nohup python -u main.py --base_asset FDUSD --initial_quote 1000 --buy_price 0.9999 > logs/2.log 2>&1 &
# nohup python -u main.py --base_asset FDUSD --initial_quote 1000 --buy_price 1.0000 > logs/3.log 2>&1 &
# nohup python -u main.py --base_asset FDUSD --initial_quote 1000 --buy_price 1.0001 > logs/4.log 2>&1 &
nohup python -u main.py --base_asset USDC --initial_quote 1000 --buy_price 0.9998 > logs/5.log 2>&1 &
nohup python -u main.py --base_asset USDC --initial_quote 1000 --buy_price 0.9999 > logs/6.log 2>&1 &
nohup python -u main.py --base_asset USDC --initial_quote 1000 --buy_price 1.0000 > logs/7.log 2>&1 &
nohup python -u main.py --base_asset USDC --initial_quote 1000 --buy_price 1.0001 > logs/8.log 2>&1 &
