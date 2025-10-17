# Python_Prj - Python Libraries Learning Repository

## Purpose

This repository is dedicated to learning and exploring multiple Python libraries through practical, hands-on projects. Each project demonstrates the usage of different Python libraries and frameworks, helping to build proficiency in various aspects of Python programming.

## Projects Overview

### 1. Alarm Clock (`/Alarm`)
A simple alarm clock application demonstrating:
- **Libraries**: `playsound`, `time`
- **Features**: 
  - Countdown timer with real-time display
  - Plays audio alert when timer expires
  - Terminal-based interface with ANSI escape codes

### 2. Socket Programming (`/Socket_Learning`)
Network programming examples with client-server architecture:
- **Libraries**: `socket`, `threading`
- **Features**:
  - Multi-threaded server handling multiple client connections
  - TCP/IP socket communication
  - Message broadcasting and connection management
  - Includes compiled executables for distribution

### 3. Password Security (`/Hashing Passwords`)
Comprehensive password security and generation tools:

#### Password Hashing
- **Libraries**: `bcrypt`, `argon2`
- **Features**:
  - Secure password hashing with bcrypt
  - Argon2 password hashing (modern, memory-hard algorithm)
  - Password verification functions

#### Password Generation
- **Libraries**: `secrets`, `string`, `pathlib`, `customtkinter`, `tkinter`
- **Features**:
  - Cryptographically secure random password generation
  - Customizable character sets (lowercase, uppercase, digits, symbols)
  - GUI application with modern dark theme
  - AI-style password generation with keywords
  - Brute-force password testing utilities
  - Batch password generation and file export

#### Web Application
- **Libraries**: `flask`, `sqlite3`, `werkzeug`
- **Features**:
  - User registration and authentication system
  - SQLite database integration
  - Secure password storage with hashing
  - Session management
  - Web-based dashboard

### 4. Basic Python (`/hello.py`)
Simple introductory Python script demonstrating basic syntax and loops.

## Getting Started

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/rayan3230/Python_Prj.git
cd Python_Prj
```

2. Install project-specific requirements (example for Password Generation GUI):
```bash
cd "Hashing Passwords/Generation"
pip install -r requirements.txt
```

### Running the Projects

#### Alarm Clock
```bash
cd Alarm
python Alarm_clock.py
```

#### Socket Programming
In one terminal (server):
```bash
cd Socket_Learning
python server.py
```

In another terminal (client):
```bash
cd Socket_Learning
python client.py
```

#### Password Hashing Examples
```bash
cd "Hashing Passwords"
python bcryptHashing.py
# or
python Argon2Hashing.py
```

#### Password Generator (CLI)
```bash
cd "Hashing Passwords/Generation"
python PasswordGeneration.py
```

#### Password Generator (GUI)
```bash
cd "Hashing Passwords/Generation"
python gui_password_generator.py
```

#### Web Application
```bash
cd "Hashing Passwords/Generation/WebFiles"
python app.py
```
Then navigate to `http://localhost:5000` in your web browser.

## Key Learning Topics

- **Network Programming**: Sockets, threading, client-server architecture
- **Security**: Cryptographic hashing, secure password storage, authentication
- **GUI Development**: tkinter, customtkinter for modern interfaces
- **Web Development**: Flask framework, SQLite databases, session management
- **Best Practices**: Secure random generation, input validation, error handling
- **File I/O**: Reading and writing files, path management

## Libraries Used

- `playsound` - Audio playback
- `time` - Time-related functions
- `socket` - Network programming
- `threading` - Concurrent execution
- `bcrypt` - Password hashing
- `argon2` - Modern password hashing
- `secrets` - Cryptographically secure random numbers
- `string` - String manipulation
- `pathlib` - Object-oriented filesystem paths
- `customtkinter` - Modern GUI framework
- `tkinter` - Standard Python GUI toolkit
- `flask` - Web application framework
- `sqlite3` - Database management
- `werkzeug` - WSGI utilities for Flask

## Project Structure

```
Python_Prj/
├── Alarm/                      # Alarm clock application
├── Socket_Learning/            # Socket programming examples
├── Hashing Passwords/          # Password security projects
│   ├── Generation/            # Password generation tools
│   │   ├── BruteForce/       # Brute-force testing utilities
│   │   └── WebFiles/         # Flask web application
│   ├── bcryptHashing.py
│   └── Argon2Hashing.py
├── hello.py                    # Basic Python example
└── README.md                   # This file
```

## Contributing

This is a personal learning repository. Feel free to fork and use these examples for your own learning purposes.

## License

This project is for educational purposes.
