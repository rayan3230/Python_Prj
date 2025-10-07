# password_generator.py
import secrets
import string
from typing import List, Union
from pathlib import Path
import datetime

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


def write_passwords_to_file(passwords: List[str], file_path: Union[str, Path], add_timestamp: bool = True) -> None:
    """Append the given passwords to file_path. Creates file and parent dirs if needed.

    Each password is written on its own line. If add_timestamp is True a small header
    with ISO timestamp is added before the block.
    """
    p = Path(file_path)
    if not p.parent.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        if add_timestamp:
            f.write(f"\n# Generated on {datetime.datetime.now().isoformat()} - {len(passwords)} passwords\n")
        for pw in passwords:
            f.write(pw + "\n")


if __name__ == "__main__":
    # Interactive prompt to choose character classes and symbol options
    def prompt_bool(prompt: str, default: bool = True) -> bool:
        hint = "Y/n" if default else "y/N"
        resp = input(f"{prompt} ({hint}): ").strip().lower()
        if not resp:
            return default
        return resp[0] in ("y", "1", "t")

    def choose_symbol_set() -> tuple[bool, str]:
        """Return a tuple (use_full_punctuation, extra_symbols).

        - If use_full_punctuation is True, we'll include string.punctuation.
        - Otherwise extra_symbols holds the custom/safe set (may be empty).
        """
        print("Choose symbols to include:")
        print("  1) No symbols")
        print("  2) Common safe set: !@#$%&*()-_=+")
        print("  3) All punctuation (full set)")
        print("  4) Custom symbols (you type them)")
        choice = input("Enter choice [2]: ").strip()
        if choice == "" or choice == "2":
            return False, "!@#$%&*()-_=+"
        if choice == "1":
            return False, ""
        if choice == "3":
            return True, ""
        if choice == "4":
            s = input("Enter the symbols to include (e.g. @#$): ")
            # deduplicate while preserving order
            return False, "".join(dict.fromkeys(s))
        # fallback
        return False, "!@#$%&*()-_=+"

    print("\nPassword generator — interactive options")
    use_lower = prompt_bool("Include lowercase letters?", True)
    use_upper = prompt_bool("Include uppercase letters?", True)
    use_digits = prompt_bool("Include digits?", True)
    include_symbols = prompt_bool("Include symbols?", False)

    use_symbols_flag = False
    extra_symbols = ""
    if include_symbols:
        use_symbols_flag, extra_symbols = choose_symbol_set()

    if not (use_lower or use_upper or use_digits or include_symbols):
        print("Error: at least one character class must be selected.")
        raise SystemExit(1)

    # Build charset: if use_symbols_flag is True we include the full punctuation set
    # otherwise pass the chosen extra_symbols to include that subset.
    charset = build_charset(
        use_lower=use_lower,
        use_upper=use_upper,
        use_digits=use_digits,
        use_symbols=use_symbols_flag,
        extra_symbols=extra_symbols,
    )

    # Get counts
    try:
        nbr = int(input("How many passwords to generate?: ").strip())
    except ValueError:
        print("Invalid number, defaulting to 1")
        nbr = 1
    try:
        length = int(input("Enter the length of the passwords: ").strip())
    except ValueError:
        print("Invalid length, defaulting to 12")
        length = 12

    pw_list = generate_many(nbr, length, charset)
    for i, p in enumerate(pw_list, 1):
        print(f"{i}: {p}")

    # Append to passwords.txt next to this script; do not overwrite on restart
    out_file = Path(__file__).resolve().parent / "passwords.txt"
    write_passwords_to_file(pw_list, out_file)
    print(f"Appended {len(pw_list)} passwords to {out_file}")
