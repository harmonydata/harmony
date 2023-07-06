from hashlib import sha256


def get_hash_value(text: str) -> str:
    """Get hash value"""

    return sha256(text.encode()).hexdigest()
