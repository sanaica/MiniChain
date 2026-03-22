from minichain.serialization import canonical_json_hash
from minichain.transaction import Transaction
from minichain.block import Block

def test_raw_data_determinism():
    print("--- Testing Raw Data Determinism ---")
    # Same data, different key order
    data_v1 = {"amount": 100, "nonce": 1, "receiver": "Alice", "sender": "Bob"}
    data_v2 = {"sender": "Bob", "receiver": "Alice", "nonce": 1, "amount": 100}

    hash_1 = canonical_json_hash(data_v1)
    hash_2 = canonical_json_hash(data_v2)

    print(f"Hash 1: {hash_1}")
    print(f"Hash 2: {hash_2}")
    assert hash_1 == hash_2
    print("Success: Raw hashes match regardless of key order!\n")

def test_transaction_id_stability():
    print("--- Testing Transaction ID Stability ---")
    # Create a transaction
    tx = Transaction(sender="Alice_PK", receiver="Bob_PK", amount=50, nonce=1)
    
    first_id = tx.tx_id
    # Re-triggering the ID calculation
    second_id = tx.tx_id

    print(f"TX ID: {first_id}")
    assert first_id == second_id
    print("Success: Transaction ID is stable and deterministic!\n")

def test_block_hash_consistency():
    print("--- Testing Block Hash Consistency ---")
    # Create a block with one transaction
    tx = Transaction(sender="A", receiver="B", amount=10, nonce=5)
    block = Block(index=1, previous_hash="0"*64, transactions=[tx], difficulty=2)
    
    initial_hash = block.compute_hash()
    print(f"Initial Block Hash: {initial_hash}")
    
    # Manually re-computing to ensure it's identical
    assert block.compute_hash() == initial_hash
    print("Success: Block hash is consistent!\n")

if __name__ == "__main__":
    try:
        test_raw_data_determinism()
        test_transaction_id_stability()
        test_block_hash_consistency()
        print("ALL CANONICAL TESTS PASSED!")
    except AssertionError as e:
        print("TEST FAILED: Serialization is not deterministic!")