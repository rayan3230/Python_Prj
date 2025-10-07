# Quick Start Guide - Distributed Password Testing

## Overview
This system allows you to distribute password testing tasks across multiple clients. The server sends URL, username, and password lists to clients, which automatically run the tests and send results back.

## Quick Setup (Local Testing)

### 1. Start the Web Application (Terminal 1)

```bash
cd ../WebFiles
python app.py
```

Leave this running. The web app will be available at http://127.0.0.1:5000

### 2. Start the Server (Terminal 2)

```bash
python distributed_server.py
```

The server will start listening on port 5051.

### 3. Start a Client (Terminal 3)

```bash
python distributed_client.py
```

When prompted:
- Server IP: Press Enter (uses 127.0.0.1)
- Server port: Press Enter (uses 5051)
- Client name: Enter a name or press Enter for auto

### 4. Send a Task from Server

Go back to Terminal 2 (server) and type:

```
server> list
```

You should see your connected client. Now send a task:

```
server> broadcast
Target URL [http://127.0.0.1:5000/login]: [Press Enter]
Username: admin
Password file path: sample_passwords.txt
```

### 5. Watch the Client Execute

Switch to Terminal 3 (client) and watch it:
- Receive the task
- Test each password
- Send results back to server

### 6. Check Results

Results are saved in `server_logs/` directory:
- `client_<name>_<timestamp>.json` - JSON format
- `client_<name>_<timestamp>.txt` - Human-readable format

## Testing with Multiple Clients

Open additional terminals and run:

```bash
python distributed_client.py
```

Use different client names to distinguish them. When you broadcast from the server, all clients will receive and execute the task.

## Network Setup (Multiple Machines)

### On Server Machine:

1. Find your IP address:
   ```bash
   ip addr show  # Linux
   ipconfig      # Windows
   ```

2. Start the server:
   ```bash
   python distributed_server.py
   ```

3. Make sure port 5051 is open in your firewall

### On Client Machines:

1. Start the client:
   ```bash
   python distributed_client.py
   ```

2. Enter the server's IP address when prompted

3. Client will automatically connect and wait for tasks

## Common Commands

### Server Commands:
- `list` - Show connected clients
- `send <ip>` - Send task to specific client
- `broadcast` - Send task to all clients
- `quit` - Stop server

### Creating Test Users in Web App:

1. Go to http://127.0.0.1:5000
2. Click "Sign Up"
3. Create a user (e.g., username: admin, password: admin123)
4. Now you can test against this user

## Example: Complete Test Run

```bash
# Terminal 1: Web App
cd ../WebFiles
python app.py

# Terminal 2: Server
python distributed_server.py
# Wait for prompt, then:
server> list
server> broadcast
# Enter: admin, sample_passwords.txt

# Terminal 3: Client 1
python distributed_client.py
# Enter defaults or custom name

# Terminal 4: Client 2 (optional)
python distributed_client.py
# Enter different name

# Back to Terminal 2 to see results
server> list
# Check server_logs/ directory for results
```

## Tips

1. **Test Locally First**: Use 127.0.0.1 to test everything on one machine
2. **Password Files**: One password per line, text files only
3. **Multiple Clients**: Each client gets a copy of all passwords
4. **Stop After First**: Default behavior stops testing after finding correct password
5. **Logs**: Check `server_logs/` for detailed results

## Troubleshooting

**Client won't connect:**
- Check server is running
- Verify IP address and port
- Check firewall settings

**No tasks received:**
- Ensure client shows as connected (`list` command)
- Try sending task with `send` command instead of `broadcast`

**Web app errors:**
- Make sure Flask app is running
- Create a test user first
- Check URL is correct (http://127.0.0.1:5000/login)

## What Happens Automatically

1. ✅ Client connects to server
2. ✅ Server sends URL, username, and password list
3. ✅ Client receives task and starts testing
4. ✅ Client tests each password against the web app
5. ✅ Client sends detailed logs back to server
6. ✅ Server saves results to files

**You just need to:**
- Start server and clients
- Send the task from server console
- Check results in `server_logs/`

## Security Reminder

⚠️ Only test systems you own or have permission to test!
