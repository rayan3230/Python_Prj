"""
GUI password generator with a local "AI-style" heuristic generator.

This file replaces the previous messy version with a clean, single-class GUI.
The "AI-style" option produces memorable-ish passwords based on user keywords
and simple transformations (capitalization, leet-speak, inserting symbols,
appending numbers). No external network calls are made.
"""

from __future__ import annotations

import secrets
import string
import sys
from pathlib import Path
from typing import List

import customtkinter as ctk
import tkinter.messagebox as mb
from tkinter import filedialog

from PasswordGeneration import build_charset, generate_many, write_passwords_to_file


SAFE_SYMBOLS = "!@#$%&*()-_=+"


def _apply_leet(s: str) -> str:
    mapping = str.maketrans({"a": "4", "e": "3", "i": "1", "o": "0", "s": "$", "t": "7"})
    return s.translate(mapping)


def _insert_symbol_between(words: List[str], symbols: str) -> str:
    sep = secrets.choice(symbols) if symbols else ""
    return sep.join(words)


def generate_ai_passwords(keywords: List[str], n: int, max_length: int, *, capitalize: bool = True,
                          leet: bool = True, insert_symbols: bool = True, symbols: str = SAFE_SYMBOLS,
                          append_numbers: bool = True) -> List[str]:
    """Generate n passwords from keywords using simple heuristic transforms.

    This is a local heuristic 'AI-style' generator — no external API used.
    """
    if not keywords:
        raise ValueError("No keywords provided for AI-style generation")
    out: List[str] = []
    kw = [k.strip() for k in keywords if k.strip()]
    if not kw:
        raise ValueError("No valid keywords entered")

    for _ in range(n):
        # pick 1 or 2 keywords
        parts = [secrets.choice(kw)]
        if secrets.randbelow(100) < 40 and len(kw) > 1:
            # 40% chance to combine two words
            other = secrets.choice(kw)
            if other != parts[0]:
                parts.append(other)

        # optionally insert symbol between parts
        pwd = _insert_symbol_between(parts, symbols) if insert_symbols and len(parts) > 1 else "".join(parts)

        # apply capitalization or leet
        if capitalize and secrets.choice((True, False)):
            pwd = pwd.title()
        if leet and secrets.choice((True, False)):
            pwd = _apply_leet(pwd.lower())

        # append numbers to reach a desired length or by chance
        if append_numbers:
            # choose 1-4 digits to append
            digits = secrets.choice((1, 2, 3, 4))
            num = ''.join(secrets.choice(string.digits) for _ in range(digits))
            pwd = pwd + num

        # if result too long, truncate; if too short, pad with safe symbols/digits
        if len(pwd) > max_length:
            pwd = pwd[:max_length]
        while len(pwd) < max_length:
            # pad with a mix of letters/digits/symbols
            choice = secrets.choice((string.ascii_letters, string.digits, symbols))
            pwd += secrets.choice(choice)

        out.append(pwd)
    return out


class PasswordGeneratorGUI(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Password Generator — GUI")
        self.geometry("900x560")
        self.minsize(760, 480)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_controls()
        self._build_results()

        # ensure clean exit
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_controls(self) -> None:
        # Use a scrollable frame so controls remain reachable on small windows
        left = ctk.CTkScrollableFrame(master=self, corner_radius=8, width=320)
        left.grid(row=0, column=0, sticky="nsew", padx=(12, 8), pady=12)
        left.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(left, text="Options", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, sticky="w", pady=(4, 8))

        # Character class checkboxes
        self.var_lower = ctk.BooleanVar(value=True)
        self.var_upper = ctk.BooleanVar(value=True)
        self.var_digits = ctk.BooleanVar(value=True)
        self.var_symbols = ctk.BooleanVar(value=False)

        ctk.CTkCheckBox(left, text="Lowercase (a-z)", variable=self.var_lower).grid(row=1, column=0, sticky="w")
        ctk.CTkCheckBox(left, text="Uppercase (A-Z)", variable=self.var_upper).grid(row=2, column=0, sticky="w")
        ctk.CTkCheckBox(left, text="Digits (0-9)", variable=self.var_digits).grid(row=3, column=0, sticky="w")
        ctk.CTkCheckBox(left, text="Include symbols", variable=self.var_symbols, command=self._on_symbols_toggle).grid(row=4, column=0, sticky="w")

        # symbol options (safe/all/custom)
        self.symbol_choice = ctk.StringVar(value="safe")
        frame_sym = ctk.CTkFrame(left, fg_color="transparent")
        frame_sym.grid(row=5, column=0, sticky="we", pady=(8, 0))
        frame_sym.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkRadioButton(frame_sym, text="None", variable=self.symbol_choice, value="none", command=self._update_custom_entry_state).grid(row=0, column=0, sticky="w")
        ctk.CTkRadioButton(frame_sym, text="Safe", variable=self.symbol_choice, value="safe", command=self._update_custom_entry_state).grid(row=0, column=1, sticky="w")
        ctk.CTkRadioButton(left, text="All punctuation", variable=self.symbol_choice, value="all", command=self._update_custom_entry_state).grid(row=6, column=0, sticky="w", pady=(6, 0))
        self.custom_symbols = ctk.CTkEntry(left, placeholder_text="Custom symbols (e.g. @#$)")
        self.custom_symbols.grid(row=7, column=0, sticky="we", pady=(6, 0))

        # AI-style options
        ctk.CTkLabel(left, text="AI-style (heuristic)", font=ctk.CTkFont(size=14, weight="bold")).grid(row=8, column=0, sticky="w", pady=(12, 4))
        self.var_ai = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(left, text="Enable AI-style generation", variable=self.var_ai, command=self._on_ai_toggle).grid(row=9, column=0, sticky="w")

        self.ai_keywords = ctk.CTkEntry(left, placeholder_text="Keywords (comma separated): e.g. rayan,fluffy")
        self.ai_keywords.grid(row=10, column=0, sticky="we", pady=(6, 0))

        # Wordlist file controls (can pick a .txt with arbitrary/random name)
        self.wordlist_path = None
        self.wordlist: List[str] = []
        frame_file = ctk.CTkFrame(left, fg_color="transparent")
        frame_file.grid(row=11, column=0, sticky="we", pady=(8, 0))
        frame_file.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(frame_file, text="Load .txt", command=self._load_wordlist).grid(row=0, column=0, sticky="we", padx=(0, 6))
        ctk.CTkButton(frame_file, text="Pick random .txt", command=self._pick_random_wordlist).grid(row=0, column=1, sticky="we", padx=(6, 0))
        self.wordlist_label = ctk.CTkLabel(left, text="No wordlist selected", anchor="w")
        self.wordlist_label.grid(row=12, column=0, sticky="we", pady=(6, 0))

        # shift subsequent AI controls down
        frame_ai = ctk.CTkFrame(left, fg_color="transparent")
        frame_ai.grid(row=13, column=0, sticky="we", pady=(6, 0))
        frame_ai.grid_columnconfigure((0, 1), weight=1)
        self.ai_capitalize = ctk.BooleanVar(value=True)
        self.ai_leet = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(frame_ai, text="Capitalize", variable=self.ai_capitalize).grid(row=0, column=0, sticky="w")
        ctk.CTkCheckBox(frame_ai, text="Leet-speak", variable=self.ai_leet).grid(row=0, column=1, sticky="w")

        self.ai_insert_symbols = ctk.BooleanVar(value=True)
        self.ai_append_numbers = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(left, text="Insert symbols between words", variable=self.ai_insert_symbols).grid(row=14, column=0, sticky="w")
        ctk.CTkCheckBox(left, text="Append random numbers", variable=self.ai_append_numbers).grid(row=15, column=0, sticky="w")

        # Count and length
        ctk.CTkLabel(left, text="How many passwords:").grid(row=16, column=0, sticky="w", pady=(12, 0))
        self.count_var = ctk.StringVar(value="10")
        ctk.CTkEntry(left, textvariable=self.count_var).grid(row=17, column=0, sticky="we")
        ctk.CTkLabel(left, text="Max length:").grid(row=18, column=0, sticky="w", pady=(8, 0))
        self.length_var = ctk.StringVar(value="8")
        ctk.CTkEntry(left, textvariable=self.length_var).grid(row=19, column=0, sticky="we")

        # Action buttons
        btn_frame = ctk.CTkFrame(left, fg_color="transparent")
        btn_frame.grid(row=20, column=0, sticky="we", pady=(12, 0))
        btn_frame.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(btn_frame, text="Generate", command=self._on_generate).grid(row=0, column=0, padx=(0, 6), sticky="we")
        ctk.CTkButton(btn_frame, text="Copy All", command=self._on_copy).grid(row=0, column=1, padx=(6, 0), sticky="we")

  

        self._update_custom_entry_state()
        self._on_ai_toggle()

    def _build_results(self) -> None:
        right = ctk.CTkFrame(master=self, corner_radius=8)
        right.grid(row=0, column=1, sticky="nsew", padx=(12, 16), pady=10)
        # make the label area compact (row 0) and let the textbox (row 1) take most space
        right.grid_rowconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=1)
        right.grid_rowconfigure(2, weight=0)
        right.grid_columnconfigure(0, weight=1)

        # smaller label, minimal padding
        ctk.CTkLabel(right, text="Generated passwords", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, sticky="w", pady=(2, 4))
        # make the textbox the prominent, large display area
        self.textbox = ctk.CTkTextbox(right, width=520, height=360)
        self.textbox.grid(row=1, column=0, sticky="nsew", pady=(2, 6))

        bottom = ctk.CTkFrame(right, fg_color="transparent")
        bottom.grid(row=2, column=0, sticky="we", pady=(12, 0))
        bottom.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(bottom, text="Save to file", command=self._on_save).grid(row=0, column=0, padx=(0, 6), sticky="we")
        ctk.CTkButton(bottom, text="Clear", fg_color="#dc2626", hover_color="#b91c1c", command=self._on_clear).grid(row=0, column=1, padx=(6, 0), sticky="we")

    def _on_symbols_toggle(self) -> None:
        # if symbols unchecked, set choice to none
        if not self.var_symbols.get():
            self.symbol_choice.set("none")
        else:
            if self.symbol_choice.get() == "none":
                self.symbol_choice.set("safe")
        self._update_custom_entry_state()

    def _update_custom_entry_state(self) -> None:
        if self.symbol_choice.get() == "custom":
            self.custom_symbols.configure(state="normal")
        else:
            self.custom_symbols.configure(state="disabled")

    def _load_wordlist(self) -> None:
        """Open a file dialog to pick a .txt wordlist and load lines."""
        path = filedialog.askopenfilename(title="Select wordlist (.txt)", filetypes=[("Text files", "*.txt" )])
        if not path:
            return
        try:
            p = Path(path)
            lines = [l.strip() for l in p.read_text(encoding='utf-8', errors='ignore').splitlines() if l.strip()]
            self.wordlist = lines
            self.wordlist_path = p
            self.wordlist_label.configure(text=f"Loaded: {p.name} ({len(lines)} words)")
        except Exception as e:
            mb.showerror("Load failed", f"Could not load file: {e}")

    def _pick_random_wordlist(self) -> None:
        """Open a folder picker and choose a random .txt file within it."""
        folder = filedialog.askdirectory(title="Select folder containing .txt wordlists")
        if not folder:
            return
        folder_p = Path(folder)
        candidates = list(folder_p.glob('*.txt'))
        if not candidates:
            mb.showinfo("No files", "No .txt files found in that folder")
            return
        chosen = secrets.choice(candidates)
        try:
            lines = [l.strip() for l in chosen.read_text(encoding='utf-8', errors='ignore').splitlines() if l.strip()]
            self.wordlist = lines
            self.wordlist_path = chosen
            self.wordlist_label.configure(text=f"Picked: {chosen.name} ({len(lines)} words)")
        except Exception as e:
            mb.showerror("Load failed", f"Could not read file: {e}")

    def _on_ai_toggle(self) -> None:
        state = "normal" if self.var_ai.get() else "disabled"
        self.ai_keywords.configure(state=state) if hasattr(self, 'ai_keywords') else None
        self.ai_keywords.configure(state=state)
        # toggle related controls
        for var in (self.ai_capitalize, self.ai_leet, self.ai_insert_symbols, self.ai_append_numbers):
            try:
                # the CheckBox widget is already created; enable/disable by changing state property if supported
                pass
            except Exception:
                pass

    def _on_generate(self) -> None:
        # parse common options
        try:
            n = max(1, int(self.count_var.get()))
        except Exception:
            n = 1
        try:
            max_len = max(4, int(self.length_var.get()))
        except Exception:
            max_len = 12

        if self.var_ai.get():
            keywords_raw = self.ai_keywords.get().strip()
            # prepare keywords: prefer user keywords; if absent and a wordlist is loaded, pick from it
            if not keywords_raw:
                if self.wordlist:
                    # pick up to 3 random words from the loaded wordlist
                    sample_size = min(3, len(self.wordlist))
                    keywords = [secrets.choice(self.wordlist) for _ in range(sample_size)]
                else:
                    mb.showerror("AI-style: missing keywords", "Enter comma-separated keywords for AI-style generation or load a wordlist.")
                    return
            else:
                keywords = [k.strip() for k in keywords_raw.replace(';', ',').split(',') if k.strip()]
                # if a wordlist is loaded, occasionally mix in one random word to diversify
                if self.wordlist and secrets.choice((True, False)):
                    keywords.append(secrets.choice(self.wordlist))
            pw_list = generate_ai_passwords(
                keywords,
                n,
                max_len,
                capitalize=self.ai_capitalize.get(),
                leet=self.ai_leet.get(),
                insert_symbols=self.ai_insert_symbols.get(),
                symbols=(self.custom_symbols.get() if self.symbol_choice.get() == 'custom' else SAFE_SYMBOLS),
                append_numbers=self.ai_append_numbers.get(),
            )
        else:
            # build charset and generate
            use_symbols_flag = True if self.symbol_choice.get() == 'all' else False
            extra = self.custom_symbols.get() if self.symbol_choice.get() == 'custom' else (SAFE_SYMBOLS if self.symbol_choice.get() == 'safe' else "")
            charset = build_charset(use_lower=self.var_lower.get(), use_upper=self.var_upper.get(), use_digits=self.var_digits.get(), use_symbols=use_symbols_flag, extra_symbols=extra)
            pw_list = generate_many(n, max_len, charset)

        # present
        self.textbox.delete('1.0', 'end')
        for p in pw_list:
            self.textbox.insert('end', p + '\n')

        # append to file
        out_file = Path(__file__).resolve().parent / 'passwords.txt'
        write_passwords_to_file(pw_list, out_file)
        self.status.configure(text=f"Appended {len(pw_list)} passwords to {out_file.name}")

    def _on_copy(self) -> None:
        data = self.textbox.get('1.0', 'end').strip()
        if not data:
            mb.showinfo('Nothing to copy', 'Generate passwords first.')
            return
        self.clipboard_clear()
        self.clipboard_append(data)
        self.status.configure(text='Copied to clipboard')

    def _on_save(self) -> None:
        data = [line.strip() for line in self.textbox.get('1.0', 'end').splitlines() if line.strip()]
        if not data:
            mb.showinfo('Nothing to save', 'Generate passwords first.')
            return
        out_file = Path(__file__).resolve().parent / 'passwords.txt'
        write_passwords_to_file(data, out_file)
        self.status.configure(text=f"Appended {len(data)} passwords to {out_file.name}")

    def _on_clear(self) -> None:
        self.textbox.delete('1.0', 'end')
        self.status.configure(text='Cleared')

    def _on_close(self) -> None:
        if mb.askokcancel('Quit', 'Do you really want to quit?'):
            try:
                self.destroy()
            finally:
                sys.exit(0)


if __name__ == '__main__':
    app = PasswordGeneratorGUI()
    app.mainloop()

