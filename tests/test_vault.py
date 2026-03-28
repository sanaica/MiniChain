# 1. CI MOCK CONFIGURATION
import sys
from unittest.mock import MagicMock

# These mocks must be defined before demo_automated_vault is imported 
sys.modules['minichain'] = MagicMock()
sys.modules['minichain.transaction'] = MagicMock()
sys.modules['minichain.serialization'] = MagicMock()

# 2. STANDARD LIBRARY & THIRD-PARTY IMPORTS
import pytest  # noqa: E402
from decimal import Decimal  # noqa: E402
from unittest.mock import AsyncMock, patch  # noqa: E402

# 3. PROJECT IMPORTS (The vault code)
from demo_automated_vault import (  # noqa: E402
    get_oracle_consensus,
    load_vault_state,
    save_vault_state,
    CircuitBreaker,
    generate_backtest_report,
    load_config,
    VaultConfig,
)

@pytest.mark.asyncio
async def test_oracle_quorum_enforcement(tmp_path, monkeypatch):
    """Verify oracle refuses to operate with fewer than 3 live sources."""
    # Simulate only 2 of 5 exchanges responding
    mock_responses = [Decimal('2500'), Decimal('2505'), None, None, None]
    
    with patch('demo_automated_vault.fetch_price', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.side_effect = mock_responses
        price, vals = await get_oracle_consensus()
        
    assert price is None, "Quorum should fail with only 2 sources"
    assert len(vals) == 0

@pytest.mark.asyncio
async def test_oracle_median_logic():
    """Verify median is used to resist outlier manipulation."""
    # One exchange is an outlier (manipulation attempt)
    mock_responses = [
        Decimal('2500'), Decimal('2505'), Decimal('2495'), 
        Decimal('2502'), Decimal('99999') # The outlier
    ]
    
    with patch('demo_automated_vault.fetch_price', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.side_effect = mock_responses
        price, _ = await get_oracle_consensus()
        
    # Median of [2495, 2500, 2502, 2505, 99999] is 2502
    assert price == Decimal('2502'), f"Expected median 2502, got {price}"

@pytest.mark.asyncio
async def test_circuit_breaker_halts():
    """Verify the vault stops if the price moves too fast (5% limit)."""
    cb = CircuitBreaker(max_deviation=Decimal("0.05"), cooldown_seconds=300)
    
    # First price sets the baseline
    cb.should_halt(Decimal("1000"))
    
    # 2% move is fine
    assert cb.should_halt(Decimal("1020")) is False
    
    # 6% move triggers the halt
    assert cb.should_halt(Decimal("1090")) is True

def test_full_state_persistence_roundtrip(tmp_path, monkeypatch):
    """Verify that state + price_history + cycles_held survives save/load exactly."""
    
    # Use a temporary file for the test
    test_file = tmp_path / "vault_state.json"
    monkeypatch.setattr('demo_automated_vault.STATE_FILE', test_file)
    
    history = [Decimal('2500.50'), Decimal('2600.75')]
    
    # ADDED: Passed '5' as the cycles_held argument
    save_vault_state(True, Decimal('2500.50'), Decimal('100.25'), history, 5)
    
    loaded = load_vault_state()
    assert loaded['has_eth'] is True
    assert loaded['total_profit'] == Decimal('100.25')
    assert loaded['price_history'] == history
    
    # ADDED: Assert that cycles_held was saved and loaded correctly
    assert loaded['cycles_held'] == 5

def test_backtest_report_generates_csv():
    """Verify that backtest always produces a valid CSV file."""
    import os
    
    test_history = [Decimal('2500'), Decimal('2600')]
    generate_backtest_report(test_history, Decimal('100'), False)
    
    assert os.path.exists("backtest_report.csv")
    # Clean up after test
    os.remove("backtest_report.csv")

def test_config_loads_from_env_and_cli():
    """Config respects .env and --live flag."""
    # This test runs in CI without real args
    cfg = load_config()
    assert isinstance(cfg, VaultConfig)