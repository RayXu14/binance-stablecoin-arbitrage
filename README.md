# Stablecoin Arbitrage

A Python-based trading bot for stablecoin arbitrage on Binance.

## Prerequisites

- Python 3.12 or higher
- A Binance account with spot trading enabled
- Binance API Key and Secret with spot trading enabled

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/stablecoin-arbitrage.git
cd stablecoin-arbitrage
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `binance_api_ks.py` file with your API credentials:
```python
key = "your_api_key"
secret = "your_api_secret"
```

## Configuration

The bot can be configured using command-line arguments. See available options in `config.py`.

## Usage

```bash
python main.py --base_asset FDUSD --initial_quote 1000 --buy_price 0.9998
python main.py --base_asset FDUSD --initial_quote 1000 --buy_price 0.9999
python main.py --base_asset FDUSD --initial_quote 1000 --buy_price 1.0000
python main.py --base_asset FDUSD --initial_quote 1000 --buy_price 1.0001
python main.py --base_asset USDC --initial_quote 1000 --buy_price 0.9998
python main.py --base_asset USDC --initial_quote 1000 --buy_price 0.9999
python main.py --base_asset USDC --initial_quote 1000 --buy_price 1.0000
python main.py --base_asset USDC --initial_quote 1000 --buy_price 1.0001
```

## Logging

Logs are automatically saved in the `logs` directory with timestamps. Each run creates a new log file.

## Security Notes

- Never commit your API credentials to version control
- Keep your API keys secure and with minimum required permissions

## Disclaimer

This bot is for educational purposes only. Use at your own risk. The authors are not responsible for any financial losses incurred while using this software.
