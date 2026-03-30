# MiniVault Chain: Automated Smart Vault Prototype

This repository contains the working prototype for the MiniChain Smart Vault—a fault-tolerant, oracle-driven automation layer designed for decentralized economic stability.

This prototype demonstrates a 3-of-5 median oracle consensus, momentum-based analytics, and strict circuit breaker safety guards, all executing locally without a web interface.

## Prerequisites

* Python 3.11+
* `pip` (comes with Python)
* Git

## Installation

Clone the repository and install the required dependencies:

```bash
git clone -b gsoc2026-smart-vault-prototype https://github.com/sanaica/MiniChain.git
cd MiniChain
```

# Install dependencies
```bash
pip install -r requirements.txt -r requirements-dev.txt
```

# Alternatively, use the included Makefile:
```bash
make install
```

## Configuration

The vault is configured entirely via local environment variables, respecting the zero-bloat philosophy.

```bash
cp .env.example .env
```

*Edit the `.env` file to customize your risk thresholds, timeouts, and exchange URLs.*

## Usage

### 1. Run the Mock Backtest (Recommended First Run)

This runs the vault against a deterministic price sequence that simulates a market dip, recovery, and peak. **No real money is used, and no live API calls are made.**

```bash
make run-mock
# Or run directly: python demo_automated_vault.py
```

### 2. Run Against Live Exchanges

This fetches real-time concurrent prices from Binance, Kraken, Coinbase, CoinGecko, and Bybit. Strict circuit breaker and 3-of-5 quorum requirements apply.

```bash
make run-live
# Or run directly: python demo_automated_vault.py --live
```

### 3. Visualizing Performance

Once a run is complete and the backtest_report.csv is generated, you can visualize the price action and trade signals:

```bash
make plot
#or python plot_backtest.py

```

## Development & Testing

**Run the Test Suite:**

```bash
make test
# Or run directly: pytest test_vault.py -v
```

**Run Lint & Type Checks:**

```bash
make lint
# Runs: ruff check . --fix && mypy --strict demo_automated_vault.py
```

### Maintenance & Reset

To wipe old backtest reports, clear Python caches, and reset the vault state to a clean "holding cash" status:

```bash
make clean
# Or If you don't have make installed on Windows, you can run the following in PowerShell:
 Set-Content -Path vault_state.json -Value '{"has_eth": false, "last_buy_price": 0.0, "total_profit": 0.0, "cycles_held": 0}' -Encoding Ascii; Remove-Item backtest_report.csv, backtest_chart.png, *.pyc -Force -ErrorAction SilentlyContinue
```

## Configuration Reference (`.env`)

The following parameters control the vault's execution and risk management engines:

| Variable | Default | Effect | 
| :--- | :--- | :--- | 
| `MOCK_MODE` | `true` | Set `false` or use `--live` flag for live exchange mode. | 
| `BUY_THRESHOLD_LIVE` | `0.9995` | Buy when price drops 0.05% below the rolling average. | 
| `SELL_THRESHOLD_LIVE` | `1.0005` | Sell when price rises 0.05% above the rolling average. | 
| `STOP_LOSS_THRESHOLD` | `0.97` | Force sell if the asset price drops 3% below the initial buy price. | 
| `MAX_HOLD_CYCLES` | `120` | Time-stop: Forces a sell after ~30 minutes (120 cycles * 15s) to prevent indefinite bag-holding. | 
| `CIRCUIT_MAX_DEVIATION` | `0.05` | Halts trading if the price moves >5% in a single cycle. | 
| `CIRCUIT_COOLDOWN` | `300` | Cooldown period (in seconds) to wait after a circuit breaker halts trading. | 
| `ORACLE_QUORUM` | `3` | Minimum number of successful exchange feeds required to form a consensus. | 
| `ORACLE_TIMEOUT` | `5` | Maximum seconds to wait before dropping an unresponsive exchange API. | 
| `POLL_INTERVAL_LIVE` | `15` | Loop interval (in seconds) between oracle checks in live mode. | 
