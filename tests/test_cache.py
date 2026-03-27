import pytest
from minichain.transaction import Transaction
from nacl.signing import SigningKey
from nacl.encoding import HexEncoder

def test_tx_caching_efficiency():
    """
    Verifies that the expensive hashing math is only performed once
    and skipped on subsequent accesses (Memoization proof).
    """
    sk = SigningKey.generate()
    sender_hex = sk.verify_key.encode(encoder=HexEncoder).decode()
    tx = Transaction(sender=sender_hex, receiver="addr", amount=100, nonce=1)

    # 1. First Access: Calculates and caches the real hash natively
    first_hash = tx.tx_id
    
    # Prove it actually cached it internally
    assert tx._cached_tx_id == first_hash

    # 2. Modify an underlying value using our backdoor bypass
    # This bypasses the normal __setattr__ which would usually clear the cache
    object.__setattr__(tx, 'amount', 9999)

    # 3. Second Access: If caching (memoization) works perfectly, 
    # it should return the OLD cached hash, ignoring the fact we changed the amount.
    second_hash = tx.tx_id

    assert first_hash == second_hash, "Memoization failed; hash was recalculated!"
    
def test_signed_tx_is_sealed():
    """Verifies that a signed transaction clears cache, changes ID, and cannot be modified."""
    sk = SigningKey.generate()
    sender_hex = sk.verify_key.encode(encoder=HexEncoder).decode()
    tx = Transaction(sender=sender_hex, receiver="bob", amount=100, nonce=1)
    
    # 1. Grab the ID before signing
    unsigned_id = tx.tx_id
    assert tx._cached_tx_id == unsigned_id
    
    # 2. Sign it
    tx.sign(sk)
    
    # 3. Prove signing killed the old cache
    assert tx._cached_tx_id is None
    
    # 4. Prove the new ID is totally different
    signed_id = tx.tx_id
    assert signed_id != unsigned_id
    
    # 5. Prove it's locked down (Sealed)
    with pytest.raises(AttributeError, match="Transaction is sealed"):
        tx.amount = 500