# Password Generator GUI

This folder contains a modern GUI for the password generator using CustomTkinter.

Files:
- `PasswordGeneration.py` — existing generator functions and CLI.
- `gui_password_generator.py` — CustomTkinter GUI that reuses the generator and appends to `passwords.txt`.
- `requirements.txt` — lists `customtkinter`.

Quick start:

1. (Optional) Create and activate a virtual environment.
2. Install requirements:

```powershell
python -m pip install -r requirements.txt
```

3. Run the GUI:

```powershell
python .\gui_password_generator.py
```

The GUI writes/appends passwords to `passwords.txt` in this folder.
