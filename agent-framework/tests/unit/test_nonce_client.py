import time
import pytest
from prometheus_swarm.clients.nonce_client import NonceClient

def test_generate_nonce():
    """Test nonce generation returns a unique non-empty string."""
    client = NonceClient()
    nonce1 = client.generate_nonce()
    nonce2 = client.generate_nonce()
    
    assert nonce1 != nonce2
    assert isinstance(nonce1, str)
    assert len(nonce1) > 0

def test_nonce_validation():
    """Test nonce validation works correctly."""
    client = NonceClient(max_nonce_age_seconds=5)
    client_id = 'test_client'
    
    # Generate a nonce for a specific client
    nonce = client.generate_nonce(client_id)
    
    # First validation should pass
    assert client.validate_nonce(nonce, client_id) == True
    
    # Second validation of same nonce should fail (already used)
    assert client.validate_nonce(nonce, client_id) == False

def test_nonce_expiration():
    """Test nonce expiration mechanism."""
    client = NonceClient(max_nonce_age_seconds=1)
    nonce = client.generate_nonce()
    
    # Wait for nonce to expire
    time.sleep(2)
    
    # Validate should now return False
    assert client.validate_nonce(nonce) == False

def test_nonce_client_id_mismatch():
    """Test nonce validation fails with incorrect client ID."""
    client = NonceClient()
    nonce = client.generate_nonce('client1')
    
    # Validation with different client ID should fail
    assert client.validate_nonce(nonce, 'client2') == False

def test_clear_expired_nonces():
    """Test clearing of expired nonces."""
    client = NonceClient(max_nonce_age_seconds=1)
    
    # Generate multiple nonces
    nonces = [client.generate_nonce() for _ in range(5)]
    
    # Wait for nonces to expire
    time.sleep(2)
    
    # Clear expired nonces
    expired_count = client.clear_expired_nonces()
    
    assert expired_count == 5
    
    # Validate store is now empty
    assert len(client.nonce_store) == 0

def test_nonce_length_and_uniqueness():
    """Test nonce length and uniqueness across multiple generations."""
    client = NonceClient()
    
    # Generate a large number of nonces
    nonces = set(client.generate_nonce() for _ in range(1000))
    
    # Verify all nonces are unique
    assert len(nonces) == 1000
    
    # Verify each nonce is of expected length (SHA-256 hexadecimal)
    assert all(len(nonce) == 64 for nonce in nonces)