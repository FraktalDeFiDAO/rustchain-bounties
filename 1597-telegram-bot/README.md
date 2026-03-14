# RustChain Telegram Bot

Telegram bot for querying RustChain blockchain data.

## Features

- `/balance <address>` - Query RTC balance for a wallet address
- `/miners` - Get current miner information
- `/price` - Get wRTC price info
- `/health` - Check node health status

## Setup

1. Create a Telegram bot via @BotFather on Telegram
2. Get your bot token
3. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set environment variables:

```bash
export TELEGRAM_BOT_TOKEN="your-bot-token"
export RUSTCHAIN_API_BASE="https://rpc.rustchain.org"  # optional, default provided
```

4. Run the bot:

```bash
python bot.py
```

## Docker

```bash
docker build -t rustchain-telegram-bot .
docker run --env TELEGRAM_BOT_TOKEN=your-token rustchain-telegram-bot
```

## Usage

```
/balance 0x1234567890abcdef1234567890abcdef12345678
/miners
/price
/health
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| TELEGRAM_BOT_TOKEN | - | Required. Your Telegram bot token |
| RUSTCHAIN_API_BASE | https://rpc.rustchain.org | RustChain RPC endpoint |
| RUSTCHAIN_REQUEST_TIMEOUT | 10 | Request timeout in seconds |
| LOG_LEVEL | INFO | Logging level |

---

Fixes #1597
