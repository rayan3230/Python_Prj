"""
Distributed Password Testing - Server
Sends tasks (URL, username, passwords) to clients and receives logs back
"""

import socket
import threading
import json
import os
import sys
from datetime import datetime


class DistributedTestServer:
    def __init__(self, host='0.0.0.0', port=5051):
        """
        Initialize the server
        
        Args:
            host: Server host address (0.0.0.0 for all interfaces)
            port: Server port
        """
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.clients = {}  # Store connected clients: {addr: {"conn": conn, "name": name}}
        self.logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "server_logs")
        os.makedirs(self.logs_dir, exist_ok=True)
        self.lock = threading.Lock()
        
    def log(self, message):
        """Print and log server messages"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def send_json(self, conn, data):
        """Send JSON data with length header"""
        try:
            json_data = json.dumps(data).encode('utf-8')
            length = len(json_data)
            # Send length as 10-byte header
            header = str(length).zfill(10).encode('utf-8')
            conn.sendall(header + json_data)
            return True
        except Exception as e:
            self.log(f"Error sending JSON: {e}")
            return False
            
    def recv_json(self, conn):
        """Receive JSON data with length header"""
        try:
            # Receive 10-byte header
            header = b""
            while len(header) < 10:
                chunk = conn.recv(10 - len(header))
                if not chunk:
                    return None
                header += chunk
                
            length = int(header.decode('utf-8'))
            
            # Receive the JSON data
            json_data = b""
            while len(json_data) < length:
                chunk = conn.recv(min(4096, length - len(json_data)))
                if not chunk:
                    return None
                json_data += chunk
                
            return json.loads(json_data.decode('utf-8'))
        except Exception as e:
            self.log(f"Error receiving JSON: {e}")
            return None
            
    def handle_client(self, conn, addr):
        """Handle a connected client"""
        self.log(f"New connection from {addr}")
        
        try:
            # Receive client identification
            client_info = self.recv_json(conn)
            if not client_info:
                self.log(f"Failed to receive client info from {addr}")
                conn.close()
                return
                
            client_name = client_info.get("name", f"Client-{addr[0]}")
            self.log(f"Client identified as: {client_name}")
            
            with self.lock:
                self.clients[addr] = {"conn": conn, "name": client_name}
            
            # Send acknowledgment
            self.send_json(conn, {"status": "connected", "message": f"Welcome {client_name}!"})
            
            # Main communication loop
            while True:
                data = self.recv_json(conn)
                if not data:
                    break
                    
                msg_type = data.get("type")
                
                if msg_type == "ready":
                    self.log(f"{client_name} is ready for tasks")
                    self.send_json(conn, {"status": "acknowledged"})
                    
                elif msg_type == "request_task":
                    # In this implementation, tasks are sent manually via send_task_to_client
                    # For now, just acknowledge
                    self.log(f"{client_name} requested a task")
                    self.send_json(conn, {"status": "no_task", "message": "No tasks available at the moment"})
                    
                elif msg_type == "log_report":
                    # Client is sending back test results
                    self.log(f"Receiving log report from {client_name}")
                    self.handle_log_report(client_name, data.get("data", {}))
                    self.send_json(conn, {"status": "received", "message": "Log report received successfully"})
                    
                elif msg_type == "disconnect":
                    self.log(f"{client_name} disconnecting")
                    break
                    
        except Exception as e:
            self.log(f"Error handling client {addr}: {e}")
        finally:
            with self.lock:
                if addr in self.clients:
                    del self.clients[addr]
            conn.close()
            self.log(f"Connection closed: {addr}")
            
    def handle_log_report(self, client_name, report_data):
        """Save log report from client"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"client_{client_name}_{timestamp}.json"
            filepath = os.path.join(self.logs_dir, filename)
            
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=2)
                
            self.log(f"Saved log report to: {filepath}")
            
            # Also create a readable text log
            txt_filename = f"client_{client_name}_{timestamp}.txt"
            txt_filepath = os.path.join(self.logs_dir, txt_filename)
            
            with open(txt_filepath, "w", encoding="utf-8") as f:
                f.write(f"Client: {client_name}\n")
                f.write(f"Timestamp: {report_data.get('timestamp', 'N/A')}\n")
                f.write(f"Target URL: {report_data.get('target_url', 'N/A')}\n")
                f.write(f"Username: {report_data.get('username', 'N/A')}\n")
                f.write(f"Total Tested: {report_data.get('total_tested', 0)}\n")
                f.write(f"Total Succeeded: {report_data.get('total_succeeded', 0)}\n")
                f.write("="*80 + "\n\n")
                
                # Write logs
                f.write("LOGS:\n")
                f.write("-"*80 + "\n")
                for log in report_data.get('logs', []):
                    f.write(f"{log}\n")
                    
                f.write("\n" + "="*80 + "\n\n")
                
                # Write detailed results
                f.write("DETAILED RESULTS:\n")
                f.write("-"*80 + "\n")
                for result in report_data.get('results', []):
                    status = "SUCCESS" if result.get('success') else "FAIL"
                    f.write(f"{result.get('timestamp')} - {status} - {result.get('password')} "
                           f"({result.get('time_taken', 0):.2f}s) - {result.get('note')}\n")
                    
            self.log(f"Saved readable log to: {txt_filepath}")
            
        except Exception as e:
            self.log(f"Error saving log report: {e}")
            
    def send_task_to_client(self, client_addr, task_config):
        """
        Send a testing task to a specific client
        
        Args:
            client_addr: Address tuple (ip, port) of the client
            task_config: Dictionary containing:
                - target_url: URL to test
                - username: Username to test
                - passwords: List of passwords
                - stop_after_first: Boolean (optional, default True)
        """
        with self.lock:
            if client_addr not in self.clients:
                self.log(f"Client {client_addr} not found")
                return False
                
            client_info = self.clients[client_addr]
            conn = client_info["conn"]
            client_name = client_info["name"]
            
        self.log(f"Sending task to {client_name}: {task_config.get('username')}@{task_config.get('target_url')}")
        
        task_message = {
            "type": "task",
            "data": task_config
        }
        
        return self.send_json(conn, task_message)
        
    def broadcast_task(self, task_config):
        """Send task to all connected clients"""
        with self.lock:
            clients_copy = list(self.clients.items())
            
        success_count = 0
        for addr, info in clients_copy:
            if self.send_task_to_client(addr, task_config):
                success_count += 1
                
        self.log(f"Task broadcast to {success_count}/{len(clients_copy)} clients")
        return success_count
        
    def list_clients(self):
        """List all connected clients"""
        with self.lock:
            return [(addr, info["name"]) for addr, info in self.clients.items()]
            
    def start(self):
        """Start the server"""
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.log(f"Server started on {self.host}:{self.port}")
        self.log(f"Logs will be saved to: {self.logs_dir}")
        
        try:
            while True:
                conn, addr = self.server_socket.accept()
                thread = threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True)
                thread.start()
        except KeyboardInterrupt:
            self.log("Server shutting down...")
        finally:
            self.server_socket.close()


def clear_terminal():
    """Clear the terminal screen"""
    os.system('clear' if os.name == 'posix' else 'cls')


def print_banner():
    """Print the server banner"""
    clear_terminal()
    print("\n" + "╔" + "═"*78 + "╗")
    print("║" + " "*20 + "DISTRIBUTED PASSWORD TESTING SERVER" + " "*23 + "║")
    print("╚" + "═"*78 + "╝")
    print("\n📋 Available Commands:")
    print("  ┌─────────────────────────────────────────────────────────────────────────┐")
    print("  │ Client Management:                                                      │")
    print("  │   list              - List all connected clients                        │")
    print("  │   send <ip>         - Send password testing task to specific client     │")
    print("  │   broadcast         - Send task to all connected clients                │")
    print("  │                                                                          │")
    print("  │ Password Generation & Testing:                                          │")
    print("  │   generate          - Generate passwords and test (uses client resources)│")
    print("  │   gentest <ip>      - Generate & test on specific client                │")
    print("  │                                                                          │")
    print("  │ Utility:                                                                │")
    print("  │   clear             - Clear the terminal screen                         │")
    print("  │   help              - Show this help message                            │")
    print("  │   status            - Show server status and statistics                 │")
    print("  │   logs              - Show recent client logs                           │")
    print("  │   quit              - Shut down the server                              │")
    print("  └─────────────────────────────────────────────────────────────────────────┘")
    print("")


def interactive_server():
    """Run server with interactive command interface"""
    server = DistributedTestServer()
    
    # Start server in a separate thread
    server_thread = threading.Thread(target=server.start, daemon=True)
    server_thread.start()
    
    print_banner()
    
    try:
        while True:
            cmd = input("\n\033[1;36mserver>\033[0m ").strip()
            
            if not cmd:
                continue
                
            cmd_lower = cmd.lower()
            
            if cmd_lower == "quit":
                print("\n\033[1;33m🔌 Shutting down server...\033[0m")
                break
            elif cmd_lower == "clear":
                print_banner()
            elif cmd_lower == "help":
                print_banner()
            elif cmd_lower == "status":
                clients = server.list_clients()
                print("\n" + "─"*80)
                print(f"📊 Server Status:")
                print(f"   • Connected clients: {len(clients)}")
                print(f"   • Server address: {server.host}:{server.port}")
                print(f"   • Logs directory: {server.logs_dir}")
                # Count log files
                try:
                    log_files = [f for f in os.listdir(server.logs_dir) if f.endswith('.txt')]
                    print(f"   • Total log files: {len(log_files)}")
                except:
                    pass
                print("─"*80)
            elif cmd_lower == "logs":
                try:
                    log_files = sorted([f for f in os.listdir(server.logs_dir) if f.endswith('.txt')])
                    if log_files:
                        print("\n" + "─"*80)
                        print("📄 Recent Log Files (last 10):")
                        for f in log_files[-10:]:
                            print(f"   • {f}")
                        print("─"*80)
                    else:
                        print("\n⚠️  No log files found.")
                except Exception as e:
                    print(f"\n❌ Error reading logs: {e}")
            elif cmd_lower == "list":
                clients = server.list_clients()
                if clients:
                    print("\n" + "─"*80)
                    print(f"👥 Connected Clients ({len(clients)}):")
                    for idx, (addr, name) in enumerate(clients, 1):
                        print(f"   {idx}. \033[1;32m{name}\033[0m - {addr[0]}:{addr[1]}")
                    print("─"*80)
                else:
                    print("\n⚠️  No clients connected.")
            elif cmd_lower.startswith("send "):
                parts = cmd.split()
                if len(parts) < 2:
                    print("\n❌ Usage: send <ip>")
                    continue
                    
                target_ip = parts[1]
                
                # Find client by IP
                clients = server.list_clients()
                target_addr = None
                for addr, name in clients:
                    if addr[0] == target_ip:
                        target_addr = addr
                        break
                        
                if not target_addr:
                    print(f"\n❌ No client found with IP: {target_ip}")
                    continue
                    
                # Get task details
                print("\n" + "─"*80)
                print("📝 Enter Task Details:")
                target_url = input("   Target URL [http://127.0.0.1:5000/login]: ").strip() or "http://127.0.0.1:5000/login"
                username = input("   Username: ").strip()
                password_file = input("   Password file path: ").strip()
                
                if not username or not password_file:
                    print("❌ Username and password file are required!")
                    continue
                    
                try:
                    with open(password_file, 'r', encoding='utf-8') as f:
                        passwords = [line.strip() for line in f if line.strip()]
                    print(f"✅ Loaded {len(passwords)} passwords from file")
                except Exception as e:
                    print(f"❌ Error reading password file: {e}")
                    continue
                    
                task_config = {
                    "target_url": target_url,
                    "username": username,
                    "passwords": passwords,
                    "stop_after_first": True
                }
                
                if server.send_task_to_client(target_addr, task_config):
                    print(f"✅ Task sent successfully to {target_addr[0]}")
                else:
                    print("❌ Failed to send task")
                print("─"*80)
                    
            elif cmd_lower == "broadcast":
                clients = server.list_clients()
                if not clients:
                    print("\n⚠️  No clients connected.")
                    continue
                    
                # Get task details
                print("\n" + "─"*80)
                print("📡 Enter Task Details for Broadcast:")
                target_url = input("   Target URL [http://127.0.0.1:5000/login]: ").strip() or "http://127.0.0.1:5000/login"
                username = input("   Username: ").strip()
                password_file = input("   Password file path: ").strip()
                
                if not username or not password_file:
                    print("❌ Username and password file are required!")
                    continue
                    
                try:
                    with open(password_file, 'r', encoding='utf-8') as f:
                        passwords = [line.strip() for line in f if line.strip()]
                    print(f"✅ Loaded {len(passwords)} passwords from file")
                except Exception as e:
                    print(f"❌ Error reading password file: {e}")
                    continue
                    
                task_config = {
                    "target_url": target_url,
                    "username": username,
                    "passwords": passwords,
                    "stop_after_first": True
                }
                
                count = server.broadcast_task(task_config)
                print(f"✅ Task broadcast to {count} client(s)")
                print("─"*80)
                
            elif cmd_lower == "generate" or cmd_lower.startswith("gentest"):
                clients = server.list_clients()
                
                # Determine target client
                target_addr = None
                if cmd_lower.startswith("gentest "):
                    parts = cmd.split()
                    if len(parts) < 2:
                        print("\n❌ Usage: gentest <ip>")
                        continue
                    target_ip = parts[1]
                    for addr, name in clients:
                        if addr[0] == target_ip:
                            target_addr = addr
                            break
                    if not target_addr:
                        print(f"\n❌ No client found with IP: {target_ip}")
                        continue
                else:
                    if not clients:
                        print("\n⚠️  No clients connected.")
                        continue
                    if len(clients) == 1:
                        target_addr = clients[0][0]
                    else:
                        print("\n👥 Multiple clients available. Choose one:")
                        for idx, (addr, name) in enumerate(clients, 1):
                            print(f"   {idx}. {name} ({addr[0]})")
                        choice = input("Enter number: ").strip()
                        try:
                            idx = int(choice) - 1
                            target_addr = clients[idx][0]
                        except:
                            print("❌ Invalid choice")
                            continue
                
                # Get password generation options
                print("\n" + "─"*80)
                print("🔐 Password Generation & Testing Configuration:")
                print("\n📋 Generation Mode:")
                print("   1. Random (character-based)")
                print("   2. AI-style (keyword-based, heuristic)")
                mode = input("Select mode [1]: ").strip() or "1"
                
                gen_config = {}
                
                if mode == "2":
                    # AI-style generation
                    print("\n🤖 AI-Style Options:")
                    keywords = input("   Keywords (comma-separated): ").strip()
                    if not keywords:
                        print("❌ Keywords are required for AI-style generation!")
                        continue
                    gen_config["mode"] = "ai"
                    gen_config["keywords"] = [k.strip() for k in keywords.split(",")]
                    
                    capitalize = input("   Capitalize words? [Y/n]: ").strip().lower()
                    gen_config["capitalize"] = capitalize != "n"
                    
                    leet = input("   Apply leet-speak? [Y/n]: ").strip().lower()
                    gen_config["leet"] = leet != "n"
                    
                    insert_symbols = input("   Insert symbols between words? [Y/n]: ").strip().lower()
                    gen_config["insert_symbols"] = insert_symbols != "n"
                    
                    append_numbers = input("   Append random numbers? [Y/n]: ").strip().lower()
                    gen_config["append_numbers"] = append_numbers != "n"
                    
                    if gen_config["insert_symbols"]:
                        symbols = input("   Symbol set [!@#$%&*()-_=+]: ").strip() or "!@#$%&*()-_=+"
                        gen_config["symbols"] = symbols
                else:
                    # Random generation
                    print("\n🎲 Random Generation Options:")
                    gen_config["mode"] = "random"
                    
                    use_lower = input("   Include lowercase (a-z)? [Y/n]: ").strip().lower()
                    gen_config["use_lower"] = use_lower != "n"
                    
                    use_upper = input("   Include uppercase (A-Z)? [Y/n]: ").strip().lower()
                    gen_config["use_upper"] = use_upper != "n"
                    
                    use_digits = input("   Include digits (0-9)? [Y/n]: ").strip().lower()
                    gen_config["use_digits"] = use_digits != "n"
                    
                    use_symbols = input("   Include symbols? [y/N]: ").strip().lower()
                    gen_config["use_symbols"] = use_symbols == "y"
                    
                    if gen_config["use_symbols"]:
                        print("   Symbol options:")
                        print("      1. Safe set (!@#$%&*()-_=+)")
                        print("      2. All punctuation")
                        print("      3. Custom")
                        sym_choice = input("   Select [1]: ").strip() or "1"
                        if sym_choice == "2":
                            gen_config["symbol_set"] = "all"
                        elif sym_choice == "3":
                            custom = input("   Enter custom symbols: ").strip()
                            gen_config["symbol_set"] = "custom"
                            gen_config["custom_symbols"] = custom
                        else:
                            gen_config["symbol_set"] = "safe"
                
                # Common options
                print("\n📊 Generation Parameters:")
                try:
                    count = int(input("   Number of passwords [100]: ").strip() or "100")
                except:
                    count = 100
                gen_config["count"] = count
                
                try:
                    length = int(input("   Password length [12]: ").strip() or "12")
                except:
                    length = 12
                gen_config["length"] = length
                
                # Testing options
                print("\n🌐 Testing Configuration:")
                target_url = input("   Target URL [http://127.0.0.1:5000/login]: ").strip() or "http://127.0.0.1:5000/login"
                username = input("   Username to test: ").strip()
                
                if not username:
                    print("❌ Username is required!")
                    continue
                
                stop_after = input("   Stop after first success? [Y/n]: ").strip().lower()
                stop_after_first = stop_after != "n"
                
                # Send generate-and-test task
                task_config = {
                    "type": "generate_and_test",
                    "generation": gen_config,
                    "testing": {
                        "target_url": target_url,
                        "username": username,
                        "stop_after_first": stop_after_first
                    }
                }
                
                print(f"\n🚀 Sending generation & testing task to client...")
                if server.send_task_to_client(target_addr, task_config):
                    print(f"✅ Task sent successfully!")
                else:
                    print("❌ Failed to send task")
                print("─"*80)
                
            else:
                print(f"\n❌ Unknown command: '{cmd}'. Type 'help' to see available commands.")
                
    except KeyboardInterrupt:
        print("\n\nShutting down...")


if __name__ == "__main__":
    interactive_server()
