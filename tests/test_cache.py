from minichain.transaction import Transaction
from nacl.signing import SigningKey
from nacl.encoding import HexEncoder

def test_tx_caching():
    """Verifies standard lifecycle caching: None -> Filled -> Cleared by Sign."""
    sk = SigningKey.generate()
    sender_hex = sk.verify_key.encode(encoder=HexEncoder).decode()
    
    tx = Transaction(sender=sender_hex, receiver="addr", amount=100, nonce=1)

    # 1. Initial State
    assert tx._cached_tx_id is None

    # 2. First access (triggers calculation)
    first_id = tx.tx_id
    assert tx._cached_tx_id == first_id

    # 3. Signing (must clear cache automatically via __setattr__)
    tx.sign(sk)
    assert tx._cached_tx_id is None

    # 4. Re-calculate after sign
    signed_id = tx.tx_id
    assert signed_id != first_id
    assert tx._cached_tx_id == signed_id

def test_tx_mutation_clears_cache():
    """Verifies that direct field updates also clear the cache (Bulletproof check)."""
    tx = Transaction(sender="alice", receiver="bob", amount=100, nonce=1)
    
    # 1. Fill the cache
    original_id = tx.tx_id
    assert tx._cached_tx_id is not None
    
    # 2. Mutate a field directly (e.g., changing the amount)
    tx.amount = 500
    
    # 3. ASSERT: Cache must be None immediately after mutation
    assert tx._cached_tx_id is None
    
    # 4. ASSERT: New ID must be different from the old one
    new_id = tx.tx_id
    assert new_id != original_id