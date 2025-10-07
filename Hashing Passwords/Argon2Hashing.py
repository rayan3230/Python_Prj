from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError

# Initialize hasher
ph = PasswordHasher()  # uses Argon2id with safe defaults

def hash_password(password: str) -> str:
    """Generate Argon2 hash (contains salt and parameters)."""
    return ph.hash(password)

def verify_password(stored_hash: str, plain_password: str) -> bool:
    """Return True if password matches stored hash, else False."""
    try:
        return ph.verify(stored_hash, plain_password)
    except (VerifyMismatchError, VerificationError):
        return False

# Example usage
hashed = hash_password("MyStrongP@ssword!")
print("Stored hash:", hashed)

# Later — during login
result = verify_password(hashed, "MyStrongP@ssword!")
print("Password valid:", result)  # → True

result = verify_password(hashed, "wrongpassword")
print("Password valid:", result)  # → False
