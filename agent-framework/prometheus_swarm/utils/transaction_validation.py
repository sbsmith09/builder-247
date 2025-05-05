import re
import uuid

def validate_transaction_id(transaction_id: str) -> bool:
    """
    Validate a transaction ID based on the following criteria:
    1. Must be a valid UUID (v4)
    2. Must be a string
    3. Cannot be empty or just whitespace

    Args:
        transaction_id (str): The transaction ID to validate

    Returns:
        bool: True if the transaction ID is valid, False otherwise
    """
    # Check if transaction_id is a string
    if not isinstance(transaction_id, str):
        return False

    # Check if transaction_id is not empty or just whitespace
    if not transaction_id or transaction_id.isspace():
        return False

    # Use UUID validation to check if it's a valid v4 UUID
    try:
        uuid_obj = uuid.UUID(transaction_id, version=4)
        return str(uuid_obj) == transaction_id
    except (ValueError, AttributeError):
        return False