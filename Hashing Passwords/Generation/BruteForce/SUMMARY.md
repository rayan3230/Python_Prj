# Distributed Password Testing System - Summary

## What Was Created

I've built a complete client-server architecture for distributed password testing based on your requirements. The system automatically distributes testing tasks from a server to multiple clients.

## Files Created

### Core Components (in BruteForce folder):

1. **`password_tester.py`** (NEW)
   - Headless password testing module
   - No GUI, can be called programmatically
   - Tests passwords against web login endpoints
   - Returns detailed results and logs

2. **`distributed_server.py`** (NEW)
   - Server that manages connected clients
   - Sends URL, username, and password lists to clients
   - Receives and saves logs from clients
   - Interactive console interface
   - Saves results to `server_logs/` directory

3. **`distributed_client.py`** (NEW)
   - Client that connects to server
   - Automatically receives tasks
   - Runs password testing using `password_tester.py`
   - Sends results back to server
   - No manual intervention needed once connected

4. **`sample_passwords.txt`** (NEW)
   - Sample password file for testing
   - One password per line format

### Documentation:

5. **`README_DISTRIBUTED.md`** (NEW)
   - Complete system documentation
   - Setup instructions
   - Usage examples
   - Troubleshooting guide

6. **`QUICKSTART.md`** (UPDATED)
   - Step-by-step quick start guide
   - Local and network setup instructions
   - Common commands reference

7. **`ARCHITECTURE.md`** (NEW)
   - Detailed system architecture
   - Data flow diagrams
   - Component responsibilities
   - Communication protocol details

## How It Works

### Setup Phase:
1. Start the web application (WebFiles/app.py)
2. Start the server (distributed_server.py)
3. Start client(s) (distributed_client.py)

### Execution Phase:
1. Server sends task to client(s):
   - Target URL (e.g., http://127.0.0.1:5000/login)
   - Username to test
   - List of passwords to try
   
2. Client automatically:
   - Receives the task
   - Loads the information
   - Runs password testing
   - Tests each password against the web app
   - Collects detailed logs
   
3. Server receives:
   - Complete test results
   - Logs of all attempts
   - Success/failure for each password
   - Timing information

### Results:
- Saved in `server_logs/` directory
- Two formats: JSON (machine-readable) and TXT (human-readable)
- Includes all tested passwords and results

## Key Features

✅ **Automatic Task Distribution**: Server sends URL and credentials to clients
✅ **Automatic Execution**: Clients run tests without manual intervention
✅ **Multiple Clients**: Support for multiple concurrent clients
✅ **Complete Logging**: Detailed logs sent back to server
✅ **Flexible Broadcasting**: Send to specific client or all clients
✅ **Real-time Progress**: See testing progress in real-time
✅ **Persistent Logs**: All results saved to files on server

## Quick Start

### Local Testing (Same Machine):

```bash
# Terminal 1: Web App
cd WebFiles
python app.py

# Terminal 2: Server
cd ../BruteForce
python distributed_server.py

# Terminal 3: Client
python distributed_client.py
# (Just press Enter for defaults)

# Back to Terminal 2:
server> broadcast
Target URL: [Enter]
Username: admin
Password file: sample_passwords.txt
```

### Network Testing (Multiple Machines):

**On Server Machine:**
```bash
python distributed_server.py
```

**On Each Client Machine:**
```bash
python distributed_client.py
# Enter server's IP address when prompted
```

## Example Workflow

1. **Create a test user in the web app:**
   - Go to http://127.0.0.1:5000
   - Sign up with username: `admin`, password: `admin123`

2. **Start all components:**
   - Web app running
   - Server running
   - Client(s) connected

3. **Send task from server:**
   ```
   server> broadcast
   Target URL: http://127.0.0.1:5000/login
   Username: admin
   Password file: sample_passwords.txt
   ```

4. **Watch client execute:**
   - Client receives task automatically
   - Tests each password
   - Sends results to server

5. **Check results:**
   - Look in `server_logs/` folder
   - Find `client_<name>_<timestamp>.txt`
   - See which passwords succeeded

## Differences from Original GUI

| Feature | Original GUI | New Distributed System |
|---------|-------------|----------------------|
| Interface | Tkinter GUI | Command-line (server), Headless (client) |
| Task Input | Manual file selection | Automatic from server |
| Execution | Manual button click | Automatic on task receipt |
| Results | Local file | Sent to server, saved centrally |
| Multiple Users | Not supported | Multiple clients supported |
| Network | Local only | Network-capable |

## Server Commands

- `list` - Show all connected clients
- `send <ip>` - Send task to specific client by IP
- `broadcast` - Send task to all connected clients
- `quit` - Shut down server

## Technical Details

### Communication:
- TCP sockets (port 5051 by default)
- JSON message format
- 10-byte length headers for reliable transmission

### Data Flow:
```
Server → Client: Task (URL, username, passwords)
Client → PasswordTester: Execute
PasswordTester → Web App: HTTP POST
Web App → PasswordTester: Response
PasswordTester → Client: Results
Client → Server: Log report
```

### Security Notes:
⚠️ **Only use this on systems you own or have authorization to test!**
- Network traffic is not encrypted
- Passwords are transmitted in plain text
- Logs contain sensitive information
- Use responsibly and legally

## Files Generated During Operation

```
BruteForce/
├── server_logs/              # Created by server
│   ├── client_name_20251007_123456.json
│   ├── client_name_20251007_123456.txt
│   ├── client_name_20251007_123457.json
│   └── client_name_20251007_123457.txt
```

## Requirements

```bash
pip install requests
```

That's it! The system uses only standard library modules plus `requests`.

## Troubleshooting

**Client can't connect:**
- Check server is running first
- Verify IP address and port
- Check firewall settings

**No tasks received:**
- Use `list` command to verify client is connected
- Try `send` to specific IP instead of broadcast

**Web app errors:**
- Ensure Flask app is running
- Create a test user first
- Verify URL is correct

## Next Steps

To use the system:

1. Read `QUICKSTART.md` for detailed setup instructions
2. Review `ARCHITECTURE.md` to understand the system design
3. See `README_DISTRIBUTED.md` for complete documentation

## Benefits

✅ **Distributed**: Multiple clients can work simultaneously
✅ **Automated**: No manual intervention after task is sent
✅ **Centralized**: All logs collected on server
✅ **Scalable**: Easy to add more clients
✅ **Flexible**: Works locally or over network
✅ **Comprehensive**: Detailed logging and reporting

The system is now ready to use! Start the server, connect clients, and send tasks. Everything else happens automatically.
