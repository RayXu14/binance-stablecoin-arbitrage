# Binance Stablecoin Arbitrage

A Python-based trading bot for stablecoin arbitrage on Binance.

Low profit but very low risk as long as stablecoins are stable.

Welcome to share your profit using this bot by commenting [this issue](https://github.com/RayXu14/stablecoin-arbitrage/issues/1).

Binance referral:
- code: `1052859643`
- link: https://accounts.binance.com/register?ref=1052859643

## Prerequisites

- Python 3.12 or higher
- Binance API Key and Secret with spot trading enabled
- **Stable network connection**, otherwise you will be very very very painful

### Memory Requirement
Take Ubuntu 24.04 AMD64 server for example:
| Number of Instances | Minimum Memory Required |
|:------------------:|:----------------------:|
| 1-7                | 500MB                  |
| 8+                 | 1GB+                   |
If the memory is not enough, you will get
```
binance.error.ClientError: (400, -1021, 'Timestamp for this request is outside of the recvWindow.'....
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/RayXu14/binance-stablecoin-arbitrage.git
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

## Example Usage

```bash
python main.py --base_asset USDC --initial_quote 1000 --buy_price 0.9999
```

## Logging

- Logs are automatically saved in the `logs` directory with timestamps.
- Asset changing records are saved in `records.csv`.

## Security Notes

- Never commit your API credentials to version control
- We **assume the commission fee rate is 0.00%**. This is TRUE for Binance USDCUSDT & FDUSDUSDT spot trading pairs, but if not, you should be aware of it. You should be responsible for your own investment.
- Generally, if you do not put much much money (orders will not be partially filled frequently) in one bot, it requests Binance API 1 times per second when not placing a new order and 2 times in a second when placing a new order,  much less than [the hard limit of Binance API](https://www.binance.com/en/support/faq/frequently-asked-questions-on-api-360004492232) (although there are also some other ambiguous limits like ML limits).

## Disclaimer

This bot is for educational purposes only. Use at your own risk. The authors are not responsible for any financial losses incurred while using this software.
