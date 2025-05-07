import uuid
import hashlib
import time
from typing import Dict, Optional

class NonceClient:
    """
    A client for generating and managing web client nonces.
    
    Nonces are unique, one-time tokens used to prevent replay attacks 
    and ensure request uniqueness.
    """
    
    def __init__(self, max_nonce_age_seconds: int = 3600):
        """
        Initialize the NonceClient.
        
        :param max_nonce_age_seconds: Maximum age of a nonce before it expires, defaults to 1 hour
        """
        self.nonce_store: Dict[str, Dict[str, Any]] = {}
        self.max_nonce_age = max_nonce_age_seconds
    
    def generate_nonce(self, client_id: Optional[str] = None) -> str:
        """
        Generate a unique nonce for a given client.
        
        :param client_id: Optional client identifier. If not provided, a random UUID is used.
        :return: A unique nonce string
        """
        # Use client_id or generate a new UUID if not provided
        identifier = client_id or str(uuid.uuid4())
        
        # Create a unique nonce by combining client identifier, timestamp, and random UUID
        nonce_seed = f"{identifier}:{time.time()}:{uuid.uuid4()}"
        
        # Generate a secure hash of the nonce seed
        nonce = hashlib.sha256(nonce_seed.encode()).hexdigest()
        
        # Store nonce details
        self.nonce_store[nonce] = {
            'client_id': identifier,
            'created_at': time.time(),
            'used': False
        }
        
        return nonce
    
    def validate_nonce(self, nonce: str, client_id: Optional[str] = None) -> bool:
        """
        Validate a nonce, checking its existence, age, and usage status.
        
        :param nonce: The nonce to validate
        :param client_id: Optional client identifier to match against the nonce
        :return: True if the nonce is valid, False otherwise
        """
        # Check if nonce exists
        if nonce not in self.nonce_store:
            return False
        
        nonce_info = self.nonce_store[nonce]
        
        # Check nonce age
        current_time = time.time()
        if current_time - nonce_info['created_at'] > self.max_nonce_age:
            del self.nonce_store[nonce]
            return False
        
        # Check client ID if provided
        if client_id and nonce_info['client_id'] != client_id:
            return False
        
        # Check if nonce has already been used
        if nonce_info['used']:
            return False
        
        # Mark nonce as used
        nonce_info['used'] = True
        return True
    
    def clear_expired_nonces(self) -> int:
        """
        Clear expired nonces from the store.
        
        :return: Number of nonces removed
        """
        current_time = time.time()
        expired_nonces = [
            nonce for nonce, info in self.nonce_store.items()
            if current_time - info['created_at'] > self.max_nonce_age
        ]
        
        for nonce in expired_nonces:
            del self.nonce_store[nonce]
        
        return len(expired_nonces)