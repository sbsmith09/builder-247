import uuid
import threading
import time
import pytest
from prometheus_swarm.src.transaction_validation import TransactionIDManager

def test_transaction_id_generation():
    """Test transaction ID generation"""
    manager = TransactionIDManager()
    transaction_id = manager.generate_transaction_id()
    
    # Verify it's a valid UUID v4
    assert manager.validate_transaction_id(transaction_id) is True
    
    # Verify uniqueness
    second_transaction_id = manager.generate_transaction_id()
    assert transaction_id != second_transaction_id

def test_transaction_id_validation():
    """Test various validation scenarios"""
    manager = TransactionIDManager()
    
    # Valid inputs
    valid_id = str(uuid.uuid4())
    assert manager.validate_transaction_id(valid_id) is True
    
    # Invalid inputs
    invalid_inputs = [
        None,
        '',
        '   ',
        123,
        str(uuid.uuid1()),  # Not a v4 UUID
        str(uuid.uuid3(uuid.NAMESPACE_DNS, 'example.com')),  # Not a v4 UUID
        'not-a-uuid',
        f"{valid_id}extra"  # Incorrect length
    ]
    
    for invalid_input in invalid_inputs:
        assert manager.validate_transaction_id(invalid_input) is False

def test_concurrent_transaction_id_generation():
    """Test concurrent transaction ID generation"""
    manager = TransactionIDManager()
    generated_ids = set()
    
    def generate_ids(num_ids, result_set):
        for _ in range(num_ids):
            result_set.add(manager.generate_transaction_id())
    
    # Create multiple threads generating transaction IDs
    threads = []
    results = [set() for _ in range(4)]
    
    for i in range(4):
        thread = threading.Thread(target=generate_ids, args=(100, results[i]))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    # Combine all generated IDs
    all_ids = set.union(*results)
    
    # Verify no duplicates and all are valid
    assert len(all_ids) == 400
    assert all(manager.validate_transaction_id(id_) for id_ in all_ids)

def test_transaction_id_release():
    """Test releasing transaction IDs"""
    manager = TransactionIDManager()
    
    # Generate and validate a transaction ID
    transaction_id = manager.generate_transaction_id()
    assert manager.validate_transaction_id(transaction_id) is True
    
    # Release the transaction ID
    manager.release_transaction_id(transaction_id)
    
    # Verify the transaction ID is no longer in used IDs
    assert transaction_id not in manager._used_transaction_ids

def test_max_stored_ids():
    """Test maximum stored IDs limit"""
    manager = TransactionIDManager(max_stored_ids=3)
    
    # Generate more IDs than max stored
    ids = [manager.generate_transaction_id() for _ in range(5)]
    
    # Internal set should not exceed max_stored_ids
    assert len(manager._used_transaction_ids) <= 3
    
    # The most recently generated IDs should be present
    assert set(ids[-3:]) == manager._used_transaction_ids