# Network Setup Guide - Remote Access

## Testing with Friends Over the Internet

### Option 1: Using ngrok (Easiest & Safest)

**ngrok** creates a secure tunnel to your local server without port forwarding.

#### Setup:

1. **Install ngrok:**
   ```bash
   # Download from https://ngrok.com/download
   # Or on Linux:
   wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
   tar -xvzf ngrok-v3-stable-linux-amd64.tgz
   sudo mv ngrok /usr/local/bin/
   ```

2. **Sign up for free account:**
   - Go to https://ngrok.com/
   - Create free account
   - Get your auth token
   - Run: `ngrok authtoken YOUR_TOKEN`

3. **Start your server:**
   ```bash
   python distributed_server.py
   # Server running on port 5051
   ```

4. **In another terminal, start ngrok:**
   ```bash
   ngrok tcp 5051
   ```

5. **ngrok will display:**
   ```
   Forwarding  tcp://0.tcp.ngrok.io:12345 -> localhost:5051
   ```

6. **Share with your friend:**
   - Host: `0.tcp.ngrok.io`
   - Port: `12345` (the port ngrok shows)

7. **Your friend connects:**
   ```bash
   python distributed_client.py
   # Enter: 0.tcp.ngrok.io
   # Enter port: 12345
   ```

**Advantages:**
- ✅ No port forwarding needed
- ✅ No router configuration
- ✅ Works behind NAT/firewalls
- ✅ Encrypted tunnel
- ✅ Easy to stop (just close ngrok)

**Limitations:**
- Free tier has bandwidth limits
- URL changes each time (unless paid plan)

---

### Option 2: Port Forwarding (Traditional)

#### On Server Machine (You):

1. **Find your local IP:**
   ```bash
   # Linux
   ip addr show
   # or
   hostname -I
   
   # You'll see something like: 192.168.1.100
   ```

2. **Find your public IP:**
   ```bash
   curl ifconfig.me
   # or visit: https://whatismyip.com
   ```

3. **Configure your router:**
   - Log into your router admin panel (usually http://192.168.1.1)
   - Find "Port Forwarding" or "Virtual Servers" section
   - Add rule:
     - External Port: 5051
     - Internal IP: Your local IP (e.g., 192.168.1.100)
     - Internal Port: 5051
     - Protocol: TCP
   - Save and apply

4. **Configure firewall:**
   ```bash
   # Linux (ufw)
   sudo ufw allow 5051/tcp
   
   # Or iptables
   sudo iptables -A INPUT -p tcp --dport 5051 -j ACCEPT
   ```

5. **Start server:**
   ```bash
   python distributed_server.py
   ```

#### On Client Machine (Your Friend):

1. **Run client:**
   ```bash
   python distributed_client.py
   ```

2. **Enter your public IP:**
   - Server IP: (your public IP from step 2 above)
   - Port: 5051

**Security Notes:**
- ⚠️ Your server is exposed to the internet
- ⚠️ Anyone with your IP can try to connect
- ⚠️ Close the port when done testing
- ⚠️ Monitor connection attempts

---

### Option 3: VPN (Most Secure)

Use a VPN like Tailscale, ZeroTier, or Hamachi to create a virtual LAN.

#### Using Tailscale (Recommended):

1. **Install Tailscale on both machines:**
   ```bash
   # Visit: https://tailscale.com/download
   # Follow instructions for your OS
   ```

2. **On both machines:**
   ```bash
   tailscale up
   # Login to the same account on both
   ```

3. **Find Tailscale IPs:**
   ```bash
   tailscale ip -4
   # Shows your Tailscale IP (e.g., 100.x.x.x)
   ```

4. **Start server (you):**
   ```bash
   python distributed_server.py
   ```

5. **Connect client (friend):**
   ```bash
   python distributed_client.py
   # Enter your Tailscale IP (100.x.x.x)
   ```

**Advantages:**
- ✅ Encrypted peer-to-peer connection
- ✅ No port forwarding
- ✅ Works anywhere
- ✅ Persistent IPs
- ✅ Most secure option

---

## Troubleshooting

### Client Can't Connect

1. **Check server is running:**
   ```bash
   # On server machine
   netstat -tuln | grep 5051
   # Should show: 0.0.0.0:5051
   ```

2. **Check firewall:**
   ```bash
   # Test if port is accessible from outside
   # On client machine
   telnet SERVER_IP 5051
   # or
   nc -zv SERVER_IP 5051
   ```

3. **Check router port forwarding:**
   - Use online port checker: https://www.yougetsignal.com/tools/open-ports/
   - Enter your public IP and port 5051
   - Should show "open"

4. **Check ISP restrictions:**
   - Some ISPs block incoming connections
   - Try using a different port (e.g., 8080, 443)
   - Update both server and client to use new port

### Connection Drops

1. **Keep-alive packets:**
   - The current implementation doesn't have keep-alive
   - Server will detect disconnection when it tries to send

2. **Timeout issues:**
   - Long-running tasks may timeout
   - The socket stays open during password testing

### Performance Over Internet

- Password testing speed depends on:
  - Client's internet speed
  - Web app server location
  - Network latency
  - Client's processing power

---

## Testing Setup

### Quick Test (Same Machine):

```bash
# Terminal 1: Web App
cd ../WebFiles
python app.py

# Terminal 2: Server
python distributed_server.py

# Terminal 3: Client 1
python distributed_client.py
# Enter: 127.0.0.1

# Terminal 4: Client 2 (optional)
python distributed_client.py
# Enter: 127.0.0.1
```

### Local Network Test:

```bash
# Machine 1 (Server):
python distributed_server.py

# Machine 2 (Client):
python distributed_client.py
# Enter server's local IP (e.g., 192.168.1.100)
```

### Internet Test:

```bash
# Your machine (Server + ngrok):
# Terminal 1:
python distributed_server.py

# Terminal 2:
ngrok tcp 5051

# Friend's machine (Client):
python distributed_client.py
# Enter ngrok URL and port
```

---

## Security Best Practices

1. **Don't expose server directly to internet**
   - Use ngrok or VPN instead of port forwarding
   - If you must use port forwarding, close it when done

2. **Monitor connections:**
   - Use `list` command to see who's connected
   - Unknown IPs? Someone unauthorized might be connecting

3. **Use authentication (Future Enhancement):**
   - Add password/token authentication to server
   - Verify clients before accepting connections

4. **Encrypt traffic (Future Enhancement):**
   - Current implementation sends data in plain text
   - Consider using SSL/TLS for production

5. **Rate limiting:**
   - Don't test too fast against web apps
   - Respect server resources
   - Be aware of detection systems

---

## Example: Complete Remote Setup

### Scenario: You and friend on different networks

**Your Setup (Server + Web App):**
```bash
# Terminal 1: Start web app
cd WebFiles
python app.py
# Running on http://127.0.0.1:5000

# Terminal 2: Start server
cd ../BruteForce
python distributed_server.py
# Server started on 0.0.0.0:5051

# Terminal 3: Start ngrok
ngrok tcp 5051
# Forwarding tcp://0.tcp.ngrok.io:12345 -> localhost:5051
```

**Share with friend:**
- ngrok host: `0.tcp.ngrok.io`
- ngrok port: `12345`
- Web app URL: Your public IP + port 5000 (if you want them to test against your web app)

**Friend's Setup (Client):**
```bash
python distributed_client.py
# Server IP: 0.tcp.ngrok.io
# Server port: 12345
# Client name: Friend-PC
```

**You send task:**
```
server> list
Connected clients (1):
  - Friend-PC (tcp://0.tcp.ngrok.io:12345)

server> send 0.tcp.ngrok.io
Target URL: http://YOUR_PUBLIC_IP:5000/login
Username: testuser
Password file: sample_passwords.txt

Task sent!
```

**Friend's client:**
- Automatically receives task
- Tests passwords
- Sends results back to you

**Check results:**
```bash
ls server_logs/
# client_Friend-PC_20251007_123456.txt
# client_Friend-PC_20251007_123456.json
```

---

## Network Diagram

```
┌─────────────────────────────────────────┐
│         Your Machine (Server)           │
│  ┌───────────────────────────────────┐  │
│  │  distributed_server.py :5051      │  │
│  └───────────────────────────────────┘  │
│              ↕                          │
│  ┌───────────────────────────────────┐  │
│  │  ngrok tunnel                     │  │
│  │  tcp://0.tcp.ngrok.io:12345       │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
              ↕ Internet
┌─────────────────────────────────────────┐
│      Friend's Machine (Client)          │
│  ┌───────────────────────────────────┐  │
│  │  distributed_client.py            │  │
│  │  Connects to ngrok URL            │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

---

## Recommended Approach

**For quick testing with a friend:**
1. Use **ngrok** - easiest and safest
2. No router configuration needed
3. Works through firewalls
4. Easy to stop when done

**For long-term setup:**
1. Use **Tailscale VPN** - secure and persistent
2. Encrypted connection
3. No exposed ports
4. Works like a local network

**Avoid:**
- Port forwarding without security measures
- Keeping ports open when not in use
- Testing without permission on production systems

---

## Cost Comparison

| Method | Cost | Setup Difficulty | Security | Speed |
|--------|------|------------------|----------|-------|
| ngrok Free | Free | ⭐ Easy | ⭐⭐⭐ Good | ⭐⭐⭐ Fast |
| Port Forwarding | Free | ⭐⭐ Medium | ⭐ Low | ⭐⭐⭐⭐ Very Fast |
| Tailscale Free | Free | ⭐ Easy | ⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐ Very Fast |
| VPS Hosting | $5-20/mo | ⭐⭐⭐ Hard | ⭐⭐⭐ Good | ⭐⭐⭐ Fast |

---

## Next Steps

1. Choose your method (recommend ngrok for first try)
2. Set up both machines
3. Test connection with `list` command
4. Send a small task first (few passwords)
5. Check logs to verify it works
6. Scale up if needed

Need help with any specific setup? Let me know!
