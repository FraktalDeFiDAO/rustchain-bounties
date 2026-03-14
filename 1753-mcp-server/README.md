# RustChain MCP Server

MCP Server for querying RustChain blockchain data via MCP protocol.

## Features

- `get_block` - Get block information by number or hash
- `get_transaction` - Get transaction details by hash
- `get_balance` - Get account balance in RTC
- `get_latest_blocks` - Get the latest N blocks
- `get_network_status` - Get network status information

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Set the RPC URL (optional, defaults to https://rpc.rustchain.com):

```bash
export RUSTCHAIN_RPC_URL="https://rpc.rustchain.com"
```

## Usage

Run the MCP server:

```bash
python mcp_server.py
```

## MCP Tools

### get_block

Get block information by block number or hash.

```python
get_block(block_number=12345)
get_block(block_hash="0x...")
```

### get_transaction

Get transaction details by transaction hash.

```python
get_transaction(tx_hash="0x...")
```

### get_balance

Get account balance for an address.

```python
get_balance(address="0x...")
```

Returns balance in both wei and RTC.

### get_latest_blocks

Get the latest N blocks (default: 10).

```python
get_latest_blocks(count=10)
```

### get_network_status

Get network status including chain ID, latest block, and gas price.

```python
get_network_status()
```

## Integration with Claude Code

This MCP server can be used with Claude Code to query RustChain blockchain data through natural language.

---

Fixes #1753
