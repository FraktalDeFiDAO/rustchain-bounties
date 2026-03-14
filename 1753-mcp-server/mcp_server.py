#!/usr/bin/env python3

"""

RustChain MCP Server - Query RustChain blockchain data via MCP protocol

"""

import os
import json
from mcp.server.fastmcp import FastMCP

import requests

mcp = FastMCP("RustChain")

RPC_URL = os.getenv("RUSTCHAIN_RPC_URL", "https://rpc.rustchain.com")


def rpc_call(method, params):
    """Make JSON-RPC call to RustChain"""
    payload = {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}
    try:
        response = requests.post(RPC_URL, json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        return result.get("result")
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def get_block(block_number: int = None, block_hash: str = None) -> dict:
    """
    Get block information by number or hash.

    Args:
        block_number: Block number (optional)
        block_hash: Block hash (optional)

    Returns:
        Block information including transactions, timestamp, etc.
    """
    if block_number is not None:
        method = "eth_getBlockByNumber"
        params = [hex(block_number), True]
    elif block_hash:
        method = "eth_getBlockByHash"
        params = [block_hash, True]
    else:
        return {"error": "Either block_number or block_hash must be provided"}

    result = rpc_call(method, params)
    if result is None:
        return {"error": "No result returned"}
    return result


@mcp.tool()
def get_transaction(tx_hash: str) -> dict:
    """
    Get transaction details by hash.

    Args:
        tx_hash: Transaction hash

    Returns:
        Transaction information including from, to, value, gas, etc.
    """
    result = rpc_call("eth_getTransactionByHash", [tx_hash])
    if result is None:
        return {"error": "Transaction not found"}
    return result


@mcp.tool()
def get_balance(address: str) -> dict:
    """
    Get account balance.

    Args:
        address: Account address

    Returns:
        Balance in wei and RTC
    """
    result = rpc_call("eth_getBalance", [address, "latest"])
    if result is None:
        return {"error": "Could not retrieve balance"}

    balance_wei = result if result != "0x0" else "0x0"
    balance_rtc = int(balance_wei, 16) / 1e18 if balance_wei != "0x0" else 0

    return {"address": address, "balance_wei": balance_wei, "balance_rtc": balance_rtc}


@mcp.tool()
def get_latest_blocks(count: int = 10) -> list:
    """
    Get the latest N blocks.

    Args:
        count: Number of blocks to retrieve (default: 10)

    Returns:
        List of recent blocks
    """
    result = rpc_call("eth_blockNumber", [])
    if result is None:
        return {"error": "Could not get latest block number"}

    latest_block = int(result, 16)
    blocks = []

    for i in range(count):
        block_num = latest_block - i
        block_info = get_block(block_number=block_num)
        if "error" not in str(block_info):
            blocks.append(block_info)

    return blocks


@mcp.tool()
def get_network_status() -> dict:
    """
    Get network status information.

    Returns:
        Network info including chain ID, latest block, gas price, etc.
    """
    chain_id_result = rpc_call("eth_chainId", [])
    block_result = rpc_call("eth_blockNumber", [])
    gas_result = rpc_call("eth_gasPrice", [])

    if chain_id_result is None or block_result is None or gas_result is None:
        return {"error": "Could not retrieve network status"}

    chain_id = int(chain_id_result, 16)
    latest_block = int(block_result, 16)
    gas_price = int(gas_result, 16)

    return {
        "chain_id": chain_id,
        "latest_block": latest_block,
        "gas_price_wei": gas_price,
        "gas_price_gwei": gas_price / 1e9,
        "rpc_url": RPC_URL,
    }


if __name__ == "__main__":
    mcp.run()
