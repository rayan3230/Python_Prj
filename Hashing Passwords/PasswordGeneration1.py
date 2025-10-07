# password_generator.py
import secrets
import string
from typing import List

CHAR_CLASSES = {
    "lower": string.ascii_lowercase,
    "upper": string.ascii_uppercase,
    "digits": string.digits,
    "symbols": string.punctuation,  # you can override to a safer subset if needed
}

def build_charset(use_lower=True, use_upper=True, use_digits=True, use_symbols=True,
                  extra_symbols: str = "") -> str:
    cs = ""
    if use_lower: cs += CHAR_CLASSES["lower"]
    if use_upper: cs += CHAR_CLASSES["upper"]
    if use_digits: cs += CHAR_CLASSES["digits"]
    if use_symbols: cs += CHAR_CLASSES["symbols"]
    if extra_symbols:
        # allow user to add particular symbols (deduplicated)
        for ch in extra_symbols:
            if ch not in cs:
                cs += ch
    if not cs:
        raise ValueError("Character set is empty. Enable at least one class.")
    return cs

def generate_password(length: int, charset: str) -> str:
    return ''.join(secrets.choice(charset) for _ in range(length))

def generate_many(n: int, length: int, charset: str) -> List[str]:
    return [generate_password(length, charset) for _ in range(n)]

if __name__ == "__main__":
    # Example: create 5 passwords, length 14, with lower+upper+digits+restricted symbols
    charset = build_charset(use_lower=True, use_upper=True, use_digits=True,
                            use_symbols=False, extra_symbols="")
    nbr = int(input("Press Enter number for generate passwords... :"))
    length = int(input("Enter the length of the passwords: "))
    pw_list = generate_many(nbr, length, charset)
    for i, p in enumerate(pw_list, 1):
        print(f"{i}: {p}")
