# to start the web

Run the Flask app (from PowerShell) with:

    python "c:\Users\HP\Desktop\WORK\Uni Prj\Python_Prj\Hashing Passwords\Generation\WebFiles\app.py"

Access from another device on the same Wi‑Fi:

1. Find the host machine IP on the Wi‑Fi (PowerShell):

    Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias Wi-Fi

   or use ipconfig and locate the IPv4 address for the wireless adapter.

2. On the other device (phone or another PC) open a browser and visit:

    http://<HOST_IP>:5000

   Example: http://192.168.100.250:5000

3. If you can't connect, allow port 5000 through Windows Firewall (run as Administrator in PowerShell):

    New-NetFirewallRule -DisplayName "Flask 5000" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow

4. If you only want to allow the port for the current network profile (Private):

    New-NetFirewallRule -DisplayName "Flask 5000 (Private)" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow -Profile Private

Notes:
- The app is started with host=0.0.0.0 so it's reachable from other devices on the LAN.
- Keep `SECRET_KEY` secure for production and disable `debug=True` when exposing the app.
