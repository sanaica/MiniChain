from minichain.transaction import Transaction
from nacl.signing import SigningKey
from nacl.encoding import HexEncoder

def test_tx_caching():
    # 1. Setup a dummy transaction
    sk = SigningKey.generate()
    sender_hex = sk.verify_key.encode(encoder=HexEncoder).decode()
    
    tx = Transaction(
        sender=sender_hex,
        receiver="receiver_addr",
        amount=100,
        nonce=1
    )

    print(f"--- Initial State ---")
    print(f"Cache value: {tx._cached_tx_id}") # Should be None

    # 2. First access (triggers calculation)
    first_id = tx.tx_id
    print(f"\n--- After First Access ---")
    print(f"Calculated ID: {first_id}")
    print(f"Cache value: {tx._cached_tx_id}") # Should now be the hash

    # 3. Second access (should be instant)
    second_id = tx.tx_id
    print(f"\n--- After Second Access ---")
    print(f"Is it the same ID? {first_id == second_id}")
    
    # 4. Signing (should clear cache)
    print(f"\n--- Signing Transaction ---")
    tx.sign(sk)
    print(f"Cache value after sign: {tx._cached_tx_id}") # Should be None again

    # 5. Access after signing (re-calculates with signature)
    signed_id = tx.tx_id
    print(f"\n--- After Accessing Signed TX ---")
    print(f"New Signed ID: {signed_id}")
    print(f"Cache value: {tx._cached_tx_id}")
    print(f"Did ID change? {signed_id != first_id}")

if __name__ == "__main__":
    test_tx_caching()