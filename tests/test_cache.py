import pytest
from minichain.transaction import Transaction
from nacl.signing import SigningKey
from nacl.encoding import HexEncoder


def test_tx_caching():
    sk = SigningKey.generate()
    sender_hex = sk.verify_key.encode(encoder=HexEncoder).decode()
    tx = Transaction(sender=sender_hex, receiver="addr", amount=100, nonce=1)

    assert tx._cached_tx_id is None
    first_id = tx.tx_id
    assert tx._cached_tx_id == first_id
    assert tx.tx_id == first_id  # second access, same result

    tx.sign(sk)
    assert tx._cached_tx_id is None

    signed_id = tx.tx_id
    assert signed_id != first_id
    assert tx._cached_tx_id == signed_id


def test_tx_mutation_clears_cache():
    tx = Transaction(sender="alice", receiver="bob", amount=100, nonce=1)
    original_id = tx.tx_id
    assert tx._cached_tx_id is not None

    tx.amount = 500
    assert tx._cached_tx_id is None
    assert tx.tx_id != original_id

def test_signed_tx_is_sealed():
    # 1. Generate a real key
    sk = SigningKey.generate()
    # 2. Get the actual hex address for that key
    sender_hex = sk.verify_key.encode(encoder=HexEncoder).decode()
    
    # 3. Use that real address as the sender
    tx = Transaction(sender=sender_hex, receiver="bob", amount=100, nonce=1)
    
    # 4. Now the signature will be accepted
    tx.sign(sk)
    
    # 5. Assert that it is indeed sealed
    with pytest.raises(AttributeError, match="Transaction is sealed"):
        tx.amount = 500