import bcrypt

def hash_password(password: str) -> bytes:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)

def verify_password(stored_hash: bytes, plain_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), stored_hash)

# Usage
h = hash_password("MyStrongP@ssword!")
print("Stored hash:", h)

print(verify_password(h, "MyStrongP@ssword!"))  # True
print(verify_password(h, "wrongpass"))          # False

