import uuid
import secrets
import threading
from typing import Set, Optional

class TransactionIDManager:
    """
    A thread-safe transaction ID management system that ensures
    unique and cryptographically secure transaction IDs.
    """
    
    def __init__(self, max_stored_ids: int = 10000):
        """
        Initialize the transaction ID manager.
        
        Args:
            max_stored_ids (int): Maximum number of transaction IDs to store
        """
        self._used_transaction_ids: Set[str] = set()
        self._lock = threading.Lock()
        self._max_stored_ids = max_stored_ids

    def generate_transaction_id(self) -> str:
        """
        Generate a cryptographically secure transaction ID.
        
        Returns:
            str: A unique transaction ID
        """
        with self._lock:
            # Use secrets for cryptographically secure generation
            while True:
                transaction_id = str(uuid.uuid4())
                
                # Check if the ID is already used
                if transaction_id not in self._used_transaction_ids:
                    # Manage maximum stored IDs
                    if len(self._used_transaction_ids) >= self._max_stored_ids:
                        # Remove oldest ID if limit is reached
                        self._used_transaction_ids.pop()
                    
                    # Add new transaction ID
                    self._used_transaction_ids.add(transaction_id)
                    return transaction_id

    def validate_transaction_id(self, transaction_id: Optional[str]) -> bool:
        """
        Validate a transaction ID based on multiple criteria.
        
        Args:
            transaction_id (str): Transaction ID to validate
        
        Returns:
            bool: Whether the transaction ID is valid
        """
        # Check for None
        if transaction_id is None:
            return False

        # Ensure input is a string
        if not isinstance(transaction_id, str):
            return False

        # Check for empty or whitespace
        if not transaction_id or transaction_id.isspace():
            return False

        # Validate UUID format and version
        try:
            # Validate the UUID
            uuid_obj = uuid.UUID(transaction_id, version=4)
            
            # Ensure it matches the expected format
            return (
                str(uuid_obj) == transaction_id and  # Canonical format
                len(transaction_id) == 36  # Correct length
            )
        except (ValueError, AttributeError):
            return False

    def release_transaction_id(self, transaction_id: str) -> None:
        """
        Release a transaction ID, making it available for reuse.
        
        Args:
            transaction_id (str): Transaction ID to release
        """
        with self._lock:
            if transaction_id in self._used_transaction_ids:
                self._used_transaction_ids.remove(transaction_id)