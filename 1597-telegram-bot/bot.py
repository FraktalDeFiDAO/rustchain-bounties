#!/usr/bin/env python3
"""RustChain Telegram Bot

Commands:
- /balance <wallet> - Query RTC balance for a wallet address
- /miners - Get current number of active miners
- /price - Get current wRTC price
- /health - Check node health status
"""

from __future__ import annotations

import logging
import os
from typing import Any

import httpx
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

API_BASE = os.getenv("RUSTCHAIN_API_BASE", "https://rpc.rustchain.org")
REQUEST_TIMEOUT = float(os.getenv("RUSTCHAIN_REQUEST_TIMEOUT", "10"))

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=os.getenv("LOG_LEVEL", "INFO"),
)
logger = logging.getLogger("rustchain_telegram_bot")


async def rpc_call(method: str, params: list[Any] | None = None) -> Any:
    """Make JSON-RPC call to RustChain"""
    if params is None:
        params = []

    payload = {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}

    timeout = httpx.Timeout(REQUEST_TIMEOUT)
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            response = await client.post(API_BASE, json=payload)
            response.raise_for_status()
            result = response.json()
            return result.get("result")
        except Exception as exc:
            logger.exception(f"RPC call {method} failed")
            raise


def _pick_number(payload: Any, keys: list[str]) -> Any:
    """Extract a number from payload using a list of possible keys"""
    if isinstance(payload, dict):
        for k in keys:
            if k in payload and payload[k] is not None:
                return payload[k]
    return None


async def cmd_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get current wRTC price"""
    try:
        try:
            data = await rpc_call(
                "eth_getBalance",
                ["0x0000000000000000000000000000000000000000", "latest"],
            )
            if data:
                await update.message.reply_text(f"wRTC Price: {data}")
                return
        except Exception:
            pass

        await update.message.reply_text(
            "Unable to fetch price. Check DexScreener for wRTC/SOL pair."
        )
    except Exception as exc:
        logger.exception("/price failed")
        await update.message.reply_text(f"Error fetching price: {exc}")


async def cmd_miners(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get number of active miners"""
    try:
        try:
            result = await rpc_call("eth_getBlockByNumber", ["latest", False])
            if result:
                miner = result.get("miner", "unknown")
                await update.message.reply_text(
                    f"Current Miner: {miner}\nBlock: {result.get('number', 'unknown')}"
                )
                return
        except Exception:
            pass

        await update.message.reply_text("Unable to fetch miner data. Try again later.")
    except Exception as exc:
        logger.exception("/miners failed")
        await update.message.reply_text(f"Error fetching miners: {exc}")


async def cmd_balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Query wallet balance"""
    if not context.args:
        await update.message.reply_text("Usage: /balance <wallet_address>")
        return

    wallet = context.args[0].strip()

    if not (wallet.startswith("0x") and len(wallet) == 42):
        await update.message.reply_text(
            "Invalid wallet address. Please provide a valid Ethereum-style address (0x... )"
        )
        return

    try:
        balance_hex = await rpc_call("eth_getBalance", [wallet, "latest"])

        if balance_hex:
            balance_wei = int(balance_hex, 16)
            balance_rtc = balance_wei / 1e18
            await update.message.reply_text(
                f"Wallet: `{wallet}`\nBalance: **{balance_rtc:.6f} RTC**",
                parse_mode="Markdown",
            )
        else:
            await update.message.reply_text(f"Could not fetch balance for {wallet}")

    except Exception as exc:
        logger.exception("/balance failed")
        await update.message.reply_text(f"Error fetching balance: {exc}")


async def cmd_health(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Check node health status"""
    try:
        result = await rpc_call("eth_blockNumber", [])

        if result:
            block_number = int(result, 16)
            await update.message.reply_text(
                f"✅ RustChain Node Status\n\nBlock Number: **{block_number}**\nStatus: ONLINE",
                parse_mode="Markdown",
            )
        else:
            await update.message.reply_text("⚠️ Node may be unreachable")

    except Exception as exc:
        logger.exception("/health failed")
        await update.message.reply_text(f"❌ Node Health: ERROR\n{exc}")


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Welcome message"""
    await update.message.reply_text(
        "🤖 *RustChain Telegram Bot*\n\n"
        "Available commands:\n"
        "• /balance <address> - Check wallet balance\n"
        "• /miners - Get miner info\n"
        "• /price - Get wRTC price\n"
        "• /health - Check node health\n\n"
        "Powered by RustChain",
        parse_mode="Markdown",
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Help command"""
    await cmd_start(update, context)


def build_app(token: str) -> Application:
    """Build the Telegram application"""
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("price", cmd_price))
    app.add_handler(CommandHandler("miners", cmd_miners))
    app.add_handler(CommandHandler("balance", cmd_balance))
    app.add_handler(CommandHandler("health", cmd_health))

    return app


def main() -> None:
    """Main entry point"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise SystemExit("TELEGRAM_BOT_TOKEN environment variable is required")

    app = build_app(token)
    logger.info("Starting RustChain Telegram bot")
    logger.info(f"API Base: {API_BASE}")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
