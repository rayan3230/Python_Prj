# System Architecture

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         SERVER MACHINE                          │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │          distributed_server.py (Port 5051)                 │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │  • Accepts client connections                        │  │ │
│  │  │  • Stores client information                        │  │ │
│  │  │  • Sends tasks (URL, username, passwords)           │  │ │
│  │  │  • Receives and saves logs                          │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  │                         ↕ TCP Socket                       │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    server_logs/                            │ │
│  │  • client_name_timestamp.json                             │ │
│  │  • client_name_timestamp.txt                              │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘

                         ↕ Network
                         
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT MACHINE 1                         │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │            distributed_client.py                           │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │  1. Connect to server                                │  │ │
│  │  │  2. Send ready status                                │  │ │
│  │  │  3. Listen for tasks                                 │  │ │
│  │  │  4. Execute tasks automatically                      │  │ │
│  │  │  5. Send results back                                │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                            ↓                                    │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              password_tester.py                            │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │  • Creates HTTP session                              │  │ │
│  │  │  • Tests each password                               │  │ │
│  │  │  • Collects results and logs                         │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                         ↓ HTTP POST                             │
└─────────────────────────────────────────────────────────────────┘

                         ↕ Network
                         
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT MACHINE 2 (Optional)                  │
│                   (Same as Client Machine 1)                    │
└─────────────────────────────────────────────────────────────────┘

                         ↕ HTTP
                         
┌─────────────────────────────────────────────────────────────────┐
│                      WEB APPLICATION SERVER                     │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │      WebFiles/app.py (Flask - Port 5000)                   │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │  • /login endpoint                                   │  │ │
│  │  │  • Validates username/password                       │  │ │
│  │  │  • Redirects to /dashboard on success                │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                            ↕                                    │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │               users.sqlite3                                │ │
│  │  (username, password_hash)                                 │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Connection Phase
```
Client → Server: {"name": "Client-123", "timestamp": "..."}
Server → Client: {"status": "connected", "message": "Welcome!"}
Client → Server: {"type": "ready"}
```

### 2. Task Distribution Phase
```
Server Console: broadcast command
Server → Client(s): {
    "type": "task",
    "data": {
        "target_url": "http://127.0.0.1:5000/login",
        "username": "admin",
        "passwords": ["pass1", "pass2", "pass3", ...],
        "stop_after_first": true
    }
}
```

### 3. Execution Phase
```
For each password:
    Client → PasswordTester: test_password(password)
    PasswordTester → Web App: POST /login {username, password}
    Web App → PasswordTester: Response (redirect or fail)
    PasswordTester → Client: Result {success, time_taken, note}
```

### 4. Reporting Phase
```
Client → Server: {
    "type": "log_report",
    "data": {
        "username": "admin",
        "target_url": "http://127.0.0.1:5000/login",
        "total_tested": 50,
        "total_succeeded": 1,
        "results": [...],
        "logs": [...]
    }
}
Server → Client: {"status": "received"}
Server → File System: Save JSON and TXT reports
```

## Component Responsibilities

### Server (distributed_server.py)
- ✅ Accept and manage client connections
- ✅ Store client registry with names and addresses
- ✅ Read password files
- ✅ Distribute tasks to specific clients or broadcast to all
- ✅ Receive log reports from clients
- ✅ Save reports in JSON and readable text format
- ✅ Provide interactive console for commands

### Client (distributed_client.py)
- ✅ Connect to server and identify itself
- ✅ Listen for incoming tasks
- ✅ Automatically execute received tasks
- ✅ Use PasswordTester to perform actual testing
- ✅ Send complete results back to server
- ✅ Handle disconnections gracefully

### Password Tester (password_tester.py)
- ✅ Create HTTP session for testing
- ✅ Test each password against login URL
- ✅ Detect successful login (dashboard redirect)
- ✅ Collect detailed results (success, time, notes)
- ✅ Generate comprehensive logs
- ✅ Stop after first success (optional)

### Web Application (WebFiles/app.py)
- ✅ Provide login endpoint
- ✅ Validate credentials against database
- ✅ Hash passwords securely
- ✅ Redirect to dashboard on success
- ✅ Return error on failure

## Communication Protocol

### Message Format
All messages use JSON with a 10-byte length header:

```
[10 bytes: length][JSON data]
Example: "0000000042" + '{"type": "ready"}'
```

### Message Types

**Client → Server:**
- `ready` - Client is ready for tasks
- `request_task` - Request a task (not used in current implementation)
- `log_report` - Sending test results
- `disconnect` - Graceful disconnection

**Server → Client:**
- `task` - Password testing task
- `ping` - Keep-alive check
- Status responses: `connected`, `received`, `acknowledged`

## File Structure

```
BruteForce/
├── distributed_server.py      # Server script
├── distributed_client.py      # Client script
├── password_tester.py         # Headless testing module
├── password_tester_gui.py     # Original GUI version
├── sample_passwords.txt       # Sample password list
├── README_DISTRIBUTED.md      # Full documentation
├── QUICKSTART.md             # Quick start guide
├── ARCHITECTURE.md           # This file
├── server_logs/              # Created automatically
│   ├── client_*.json         # JSON reports
│   └── client_*.txt          # Text reports
└── logs/                     # GUI logs
    └── bruteforce_results_*.txt

WebFiles/
├── app.py                    # Flask web application
├── users.sqlite3            # User database
├── templates/
│   ├── login.html
│   └── dashboard.html
└── static/
    └── style.css
```

## Network Configuration

### Ports Used:
- **5051**: Server listening port (configurable)
- **5000**: Web application (Flask default)

### Firewall Rules Needed:
```bash
# On server machine, allow incoming on 5051
sudo ufw allow 5051/tcp

# On web app machine, allow incoming on 5000
sudo ufw allow 5000/tcp
```

## Scalability

### Current Implementation:
- One server, multiple clients
- Each client gets full password list
- All clients test independently
- Results aggregated on server

### Possible Enhancements:
- Distribute different password ranges to different clients
- Load balancing across clients
- Priority queue for tasks
- Real-time progress monitoring
- Web-based server dashboard
- Database storage for results

## Security Considerations

⚠️ **Important:**
- Use only on authorized systems
- Network traffic is NOT encrypted
- Consider using VPN or SSH tunnels for remote testing
- Password lists may contain sensitive data
- Logs contain tested passwords in plain text
- Implement rate limiting to avoid detection

## Error Handling

### Connection Failures:
- Client automatically attempts reconnection
- Server maintains client list, removes on disconnect
- Graceful shutdown on Ctrl+C

### Task Failures:
- Individual password failures are logged
- Network errors are captured in results
- Client continues with remaining passwords
- Results sent even if task partially fails

### Web App Issues:
- Timeouts handled (10 second default)
- HTTP errors captured and logged
- Non-redirect responses treated as failures
