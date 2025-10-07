# Server Commands Reference

## Quick Command Guide

### Client Management
```bash
list              # Show all connected clients with IP addresses
send <ip>         # Send password testing task to specific client
broadcast         # Send task to all connected clients
```

### Password Generation & Testing
```bash
generate          # Generate passwords on client and test them
                  # - Interactive mode: choose client if multiple available
                  # - Configure generation (random or AI-style)
                  # - Configure testing parameters
                  # - Client generates passwords and tests automatically

gentest <ip>      # Generate and test on specific client
                  # Same as 'generate' but targets a specific IP
```

### Utility Commands
```bash
clear             # Clear the terminal screen
help              # Show the help menu with all commands
status            # Show server status and statistics
logs              # Show recent client log files
quit              # Shut down the server gracefully
```

## Generation Modes

### 1. Random Mode (Character-based)
Generates passwords using character sets:
- **Lowercase letters** (a-z)
- **Uppercase letters** (A-Z)
- **Digits** (0-9)
- **Symbols** (optional)
  - None
  - Safe set: `!@#$%&*()-_=+`
  - All punctuation
  - Custom symbols

**Example Configuration:**
```
Mode: 1 (Random)
Include lowercase: Y
Include uppercase: Y
Include digits: Y
Include symbols: Y
  Symbol options:
    1. Safe set (!@#$%&*()-_=+)
Number of passwords: 100
Password length: 12
```

### 2. AI-Style Mode (Keyword-based, Heuristic)
Generates memorable passwords using:
- **Keywords**: Base words (comma-separated)
- **Capitalization**: Title case transformation
- **Leet-speak**: Character substitution (a→4, e→3, etc.)
- **Symbol insertion**: Between words
- **Number appending**: Random digits at the end

**Example Configuration:**
```
Mode: 2 (AI-style)
Keywords: admin,secure,login
Capitalize words: Y
Apply leet-speak: Y
Insert symbols between words: Y
  Symbol set: !@#$%&*()-_=+
Append random numbers: Y
Number of passwords: 100
Password length: 12
```

**Example Generated Passwords (AI-style):**
```
Admin@S3cur3_7891
l0gin!Secure4523
SECURE#Admin1847
admin$Login0192
```

## Full Workflow Examples

### Example 1: Simple Password Testing
```bash
server> list
Connected clients:
  1. Client-Kali - 192.168.1.100

server> send 192.168.1.100
Target URL [http://127.0.0.1:5000/login]: http://192.168.100.250:5000/login
Username: admin
Password file path: sample_passwords.txt
✅ Loaded 12 passwords from file
✅ Task sent successfully
```

### Example 2: Generate and Test (Random Mode)
```bash
server> generate
👥 Multiple clients available. Choose one:
  1. Client-Kali (192.168.1.100)
  2. Client-Desktop (192.168.1.101)
Enter number: 1

📋 Generation Mode:
  1. Random (character-based)
  2. AI-style (keyword-based)
Select mode [1]: 1

🎲 Random Generation Options:
Include lowercase (a-z)? [Y/n]: Y
Include uppercase (A-Z)? [Y/n]: Y
Include digits (0-9)? [Y/n]: Y
Include symbols? [y/N]: y
  Symbol options:
    1. Safe set (!@#$%&*()-_=+)
    2. All punctuation
    3. Custom
Select [1]: 1

📊 Generation Parameters:
Number of passwords [100]: 200
Password length [12]: 14

🌐 Testing Configuration:
Target URL [http://127.0.0.1:5000/login]: http://192.168.100.250:5000/login
Username to test: admin
Stop after first success? [Y/n]: Y

✅ Task sent successfully!
```

### Example 3: Generate and Test (AI-Style Mode)
```bash
server> gentest 192.168.1.100

📋 Generation Mode:
  1. Random (character-based)
  2. AI-style (keyword-based)
Select mode [1]: 2

🤖 AI-Style Options:
Keywords (comma-separated): password,admin,secure
Capitalize words? [Y/n]: Y
Apply leet-speak? [Y/n]: Y
Insert symbols between words? [Y/n]: Y
  Symbol set [!@#$%&*()-_=+]: !@#$
Append random numbers? [Y/n]: Y

📊 Generation Parameters:
Number of passwords [100]: 50
Password length [12]: 10

🌐 Testing Configuration:
Target URL [http://127.0.0.1:5000/login]: http://192.168.100.250:5000/login
Username to test: rayan3230
Stop after first success? [Y/n]: Y

✅ Task sent successfully!
```

### Example 4: Broadcast to All Clients
```bash
server> broadcast

📡 Enter Task Details for Broadcast:
Target URL [http://127.0.0.1:5000/login]: http://192.168.100.250:5000/login
Username: testuser
Password file path: /path/to/passwords.txt
✅ Loaded 500 passwords from file
✅ Task broadcast to 3 client(s)
```

## Client Behavior

When a client receives a task:

### Regular Testing Task:
1. Receives URL, username, and password list
2. Tests each password against the login endpoint
3. Logs all attempts (success/fail)
4. Sends complete results back to server

### Generate-and-Test Task:
1. Receives generation configuration
2. **Generates passwords** using client resources
3. **Saves generated passwords** to local file
4. Tests each generated password
5. Sends complete results back to server

## Server Logs

All client results are saved in `server_logs/` directory:

```
server_logs/
├── client_Kali_20251007_123456.json      # Machine-readable
├── client_Kali_20251007_123456.txt       # Human-readable
├── client_Desktop_20251007_123510.json
└── client_Desktop_20251007_123510.txt
```

**View recent logs:**
```bash
server> logs
📄 Recent Log Files (last 10):
  • client_Kali_20251007_123456.txt
  • client_Desktop_20251007_123510.txt
```

## Tips & Best Practices

1. **Use `status` command** to check connected clients before sending tasks
2. **Use `clear` command** to clean up the terminal for better visibility
3. **AI-style generation** works best with meaningful keywords
4. **Random generation** is faster and produces more diverse passwords
5. **Generate on client** to distribute computational load
6. **Stop after first success** to save time (recommended for testing)
7. **Check logs** regularly to review results

## Color Codes in Terminal

- 🟢 **Green** - Success messages, client names
- 🔴 **Red** - Error messages (❌)
- 🟡 **Yellow** - Warnings (⚠️)
- 🔵 **Cyan** - Command prompt (`server>`)
- ⚪ **White** - General information

## Keyboard Shortcuts

- **Ctrl+C** - Stop current command input (graceful)
- **Ctrl+D** - Exit server (emergency)
- **Up/Down arrows** - Command history (if supported by shell)

## Troubleshooting

### "No clients connected"
- Ensure clients are running and connected
- Check network connectivity
- Use `status` to verify server is running

### "Failed to send task"
- Client may have disconnected
- Use `list` to verify client is still connected
- Try reconnecting the client

### "Error reading password file"
- Check file path is correct
- Ensure file has read permissions
- Verify file contains passwords (one per line)

### Generation fails on client
- Ensure PasswordGeneration.py is in correct location
- Check client has necessary dependencies
- Review client terminal output for errors
