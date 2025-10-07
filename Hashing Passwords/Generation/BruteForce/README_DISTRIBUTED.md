# Distributed Password Testing System

A client-server architecture for distributed password testing. The server manages tasks and collects results, while clients execute the password tests.

## Overview

- **Server**: Manages connected clients, distributes testing tasks (URL, username, password list), and collects logs
- **Client**: Connects to server, receives tasks, runs password tests automatically, and sends results back
- **Password Tester**: Headless module that performs the actual password testing

## Files

### Core Components

1. **`distributed_server.py`** - Server that manages clients and distributes tasks
2. **`distributed_client.py`** - Client that receives and executes tasks
3. **`password_tester.py`** - Headless password testing module (non-GUI)
4. **`password_tester_gui.py`** - Original GUI version (still functional)

## Setup

### Requirements

Install required packages:

```bash
pip install requests
```

### WebFiles Directory

The system tests against a Flask web application located in `../WebFiles/`:
- `app.py` - Flask login application
- `users.sqlite3` - User database

To start the web application:

```bash
cd ../WebFiles
python app.py
```

The web app runs on `http://127.0.0.1:5000` by default.

## Usage

### 1. Start the Server

On the server machine:

```bash
python distributed_server.py
```

The server will:
- Listen on port 5051 (default)
- Accept client connections
- Wait for commands to distribute tasks

### Server Commands

- `list` - Show all connected clients
- `send <ip>` - Send a task to a specific client by IP address
- `broadcast` - Send the same task to all connected clients
- `quit` - Shut down the server

### 2. Start Client(s)

On each client machine:

```bash
python distributed_client.py
```

You'll be prompted for:
- Server IP address (default: 127.0.0.1)
- Server port (default: 5051)
- Client name (optional, auto-generated if not provided)

The client will:
- Connect to the server
- Send ready status
- Listen for tasks
- Execute tasks automatically when received
- Send results back to server

### 3. Send Tasks from Server

Once clients are connected, use the server console:

#### Send to Specific Client

```
server> send 192.168.1.100
Target URL [http://127.0.0.1:5000/login]: http://127.0.0.1:5000/login
Username: testuser
Password file path: ../passwords.txt
```

#### Broadcast to All Clients

```
server> broadcast
Target URL [http://127.0.0.1:5000/login]: http://127.0.0.1:5000/login
Username: admin
Password file path: passwords.txt
```

## How It Works

### Task Distribution

1. Server reads password file and task parameters
2. Server sends JSON message to client(s) with:
   - Target URL
   - Username
   - List of passwords
   - Stop-after-first flag

### Client Execution

1. Client receives task automatically
2. Creates `PasswordTester` instance
3. Tests each password against the login URL
4. Collects results and logs
5. Sends complete report back to server

### Results Collection

Server saves two files per client report:
- `client_<name>_<timestamp>.json` - Full JSON report
- `client_<name>_<timestamp>.txt` - Human-readable log

Files are saved in `server_logs/` directory.

## Example Workflow

### Terminal 1: Start Web App

```bash
cd ../WebFiles
python app.py
```

### Terminal 2: Start Server

```bash
python distributed_server.py
```

### Terminal 3: Start Client

```bash
python distributed_client.py
# Enter server details when prompted
```

### Terminal 4 (Optional): Additional Client

```bash
python distributed_client.py
# Enter same server details
```

### Back to Server Terminal

```
server> list
Connected clients (2):
  - Client-12345 (192.168.1.100:54321)
  - Client-67890 (192.168.1.101:54322)

server> broadcast
Target URL [http://127.0.0.1:5000/login]: 
Username: admin
Password file path: passwords.txt
Task broadcast to 2 client(s)
```

## Password File Format

Password files should contain one password per line:

```
password123
admin
test123
letmein
```

Empty lines are automatically filtered out.

## Security Notes

⚠️ **WARNING**: This tool is for testing systems you own or have authorization to test.

- Only use against systems you have permission to test
- Be aware of rate limiting and account lockouts
- Use responsibly and ethically

## Architecture Details

### Communication Protocol

- Uses TCP sockets for client-server communication
- JSON messages with 10-byte length headers
- Reliable message delivery

### Message Types

**Client to Server:**
- `ready` - Client is ready for tasks
- `request_task` - Client requesting a task
- `log_report` - Client sending test results
- `disconnect` - Client disconnecting

**Server to Client:**
- `task` - Server sending a testing task
- `ping` - Keep-alive check
- Status messages (acknowledged, received, etc.)

### Data Flow

```
Server → Client: Task (URL, username, passwords)
Client → PasswordTester: Execute tests
PasswordTester → WebApp: HTTP POST requests
WebApp → PasswordTester: Responses
PasswordTester → Client: Results
Client → Server: Log report
Server → File System: Save logs
```

## Troubleshooting

### Client Can't Connect

- Verify server is running
- Check IP address and port
- Ensure no firewall blocking port 5051

### No Tasks Received

- Make sure client is connected (`list` on server)
- Try sending task explicitly with `send` command

### Web App Connection Failed

- Verify web app is running on http://127.0.0.1:5000
- Check URL in task configuration
- Ensure `requests` library is installed

## Advanced Usage

### Custom Client Names

```python
from distributed_client import DistributedTestClient

client = DistributedTestClient(
    server_host="192.168.1.50",
    server_port=5051,
    client_name="TestMachine-01"
)
client.run()
```

### Programmatic Server Control

```python
from distributed_server import DistributedTestServer

server = DistributedTestServer(host='0.0.0.0', port=5051)

# Start in background
import threading
threading.Thread(target=server.start, daemon=True).start()

# Send task programmatically
task = {
    "target_url": "http://127.0.0.1:5000/login",
    "username": "admin",
    "passwords": ["pass1", "pass2", "pass3"],
    "stop_after_first": True
}
server.broadcast_task(task)
```

## License

Educational purposes only. Use responsibly.
