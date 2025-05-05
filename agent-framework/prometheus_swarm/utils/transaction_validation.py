import re
import uuid

def validate_transaction_id(transaction_id: str) -> bool:
    """
    Validate a transaction ID based on the following criteria:
    1. Must be a valid UUID (v4)
    2. Must be a string
    3. Cannot be empty or just whitespace
    4. Must match exact UUID format (case-sensitive)

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

    # Regex pattern for strict v4 UUID validation
    uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$', re.IGNORECASE)

    # Validate UUID format
    if not uuid_pattern.match(transaction_id):
        return False

    # Further validate using uuid module to ensure it's a valid v4 UUID
    try:
        uuid_obj = uuid.UUID(transaction_id, version=4)
        # Confirm the UUID is in canonical lowercase format
        return str(uuid_obj) == transaction_id.lower()
    except (ValueError, AttributeError):
        return False