# 1. Import Password Hashing Library
from pwdlib import PasswordHash

# 2. Initialize Password Hasher
password_hash = PasswordHash.recommended()

# 3. Hash a Password
def hash(password: str):
    return password_hash.hash(password)

# 4. Verify a Password
def verify(plain_password: str, hashed_password: str):
    return password_hash.verify(plain_password, hashed_password)