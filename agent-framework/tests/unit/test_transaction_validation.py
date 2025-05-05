import pytest
import uuid
from prometheus_swarm.utils.transaction_validation import validate_transaction_id

def test_valid_transaction_id():
    """Test that a valid v4 UUID passes validation"""
    valid_id = str(uuid.uuid4())
    assert validate_transaction_id(valid_id) is True

def test_invalid_transaction_id_types():
    """Test various invalid input types"""
    invalid_inputs = [
        None,
        123,
        ['not a string'],
        {'not': 'a string'},
        b'bytes',
        float('inf'),
    ]
    for invalid_input in invalid_inputs:
        assert validate_transaction_id(invalid_input) is False

def test_empty_and_whitespace_transaction_ids():
    """Test empty and whitespace transaction IDs"""
    empty_inputs = [
        '',
        '   ',
        '\t\n',
    ]
    for empty_input in empty_inputs:
        assert validate_transaction_id(empty_input) is False

def test_invalid_uuid_format():
    """Test various invalid UUID formats"""
    invalid_uuids = [
        'not-a-uuid',
        '123e4567-e89b-12d3-a456-426614174000',  # valid format but not a v4 UUID
        str(uuid.uuid1()),  # v1 UUID
        str(uuid.uuid3(uuid.NAMESPACE_DNS, 'example.com')),  # v3 UUID
        str(uuid.uuid5(uuid.NAMESPACE_DNS, 'example.com')),  # v5 UUID
    ]
    for invalid_uuid in invalid_uuids:
        assert validate_transaction_id(invalid_uuid) is False

def test_lowercase_and_uppercase_transaction_ids():
    """Test that UUIDs with different case are validated correctly"""
    test_id = str(uuid.uuid4())
    assert validate_transaction_id(test_id.lower()) is True
    assert validate_transaction_id(test_id.upper()) is True
    assert validate_transaction_id(test_id.capitalize()) is False