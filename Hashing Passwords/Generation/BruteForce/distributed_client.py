"""
Distributed Password Testing - Client
Connects to server, receives tasks, runs password tests, and sends logs back
"""

import socket
import json
import os
import sys
import secrets
import string
from datetime import datetime
from pathlib import Path
from password_tester import PasswordTester

# Add parent directory to path to import PasswordGeneration
parent_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(parent_dir))

try:
    from PasswordGeneration import build_charset, generate_many
except ImportError:
    print("Warning: Could not import PasswordGeneration module. Password generation features may not work.")
    build_charset = None
    generate_many = None


class DistributedTestClient:
    def __init__(self, server_host, server_port=5051, client_name=None):
        """
        Initialize the client
        
        Args:
            server_host: Server IP address
            server_port: Server port (default 5051)
            client_name: Custom name for this client (optional)
        """
        self.server_host = server_host
        self.server_port = server_port
        self.client_name = client_name or f"Client-{os.getpid()}"
        self.socket = None
        self.connected = False
        
    def log(self, message):
        """Print log messages"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def connect(self):
        """Connect to the server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_host, self.server_port))
            self.connected = True
            self.log(f"Connected to server at {self.server_host}:{self.server_port}")
            
            # Send client identification
            client_info = {
                "name": self.client_name,
                "timestamp": datetime.now().isoformat()
            }
            self.send_json(client_info)
            
            # Wait for acknowledgment
            ack = self.recv_json()
            if ack and ack.get("status") == "connected":
                self.log(f"Server says: {ack.get('message')}")
                return True
            else:
                self.log("Failed to receive server acknowledgment")
                return False
                
        except Exception as e:
            self.log(f"Connection error: {e}")
            self.connected = False
            return False
            
    def send_json(self, data):
        """Send JSON data with length header"""
        try:
            json_data = json.dumps(data).encode('utf-8')
            length = len(json_data)
            # Send length as 10-byte header
            header = str(length).zfill(10).encode('utf-8')
            self.socket.sendall(header + json_data)
            return True
        except Exception as e:
            self.log(f"Error sending JSON: {e}")
            return False
            
    def recv_json(self):
        """Receive JSON data with length header"""
        try:
            # Receive 10-byte header
            header = b""
            while len(header) < 10:
                chunk = self.socket.recv(10 - len(header))
                if not chunk:
                    return None
                header += chunk
                
            length = int(header.decode('utf-8'))
            
            # Receive the JSON data
            json_data = b""
            while len(json_data) < length:
                chunk = self.socket.recv(min(4096, length - len(json_data)))
                if not chunk:
                    return None
                json_data += chunk
                
            return json.loads(json_data.decode('utf-8'))
        except Exception as e:
            self.log(f"Error receiving JSON: {e}")
            return None
            
    def send_ready(self):
        """Tell server we're ready for tasks"""
        self.log("Sending ready status to server")
        message = {"type": "ready"}
        return self.send_json(message)
        
    def request_task(self):
        """Request a task from the server"""
        self.log("Requesting task from server")
        message = {"type": "request_task"}
        return self.send_json(message)
        
    def send_log_report(self, test_results):
        """
        Send test results back to server
        
        Args:
            test_results: Dictionary containing test results from PasswordTester
        """
        self.log("Sending log report to server")
        message = {
            "type": "log_report",
            "data": test_results
        }
        
        if self.send_json(message):
            # Wait for acknowledgment
            ack = self.recv_json()
            if ack and ack.get("status") == "received":
                self.log("Server acknowledged log report")
                return True
            else:
                self.log("Failed to receive acknowledgment for log report")
                return False
        return False
        
    def generate_passwords_ai(self, keywords, count, length, capitalize=True, leet=True, 
                             insert_symbols=True, symbols="!@#$%&*()-_=+", append_numbers=True):
        """Generate passwords using AI-style heuristic method"""
        def apply_leet(s):
            mapping = str.maketrans({"a": "4", "e": "3", "i": "1", "o": "0", "s": "$", "t": "7"})
            return s.translate(mapping)
        
        def insert_symbol_between(words, symbols):
            sep = secrets.choice(symbols) if symbols else ""
            return sep.join(words)
        
        passwords = []
        for _ in range(count):
            # Pick 1 or 2 keywords
            parts = [secrets.choice(keywords)]
            if secrets.randbelow(100) < 40 and len(keywords) > 1:
                other = secrets.choice(keywords)
                if other != parts[0]:
                    parts.append(other)
            
            # Insert symbol between parts
            pwd = insert_symbol_between(parts, symbols) if insert_symbols and len(parts) > 1 else "".join(parts)
            
            # Apply capitalization or leet
            if capitalize and secrets.choice((True, False)):
                pwd = pwd.title()
            if leet and secrets.choice((True, False)):
                pwd = apply_leet(pwd.lower())
            
            # Append numbers
            if append_numbers:
                digits = secrets.choice((1, 2, 3, 4))
                num = ''.join(secrets.choice(string.digits) for _ in range(digits))
                pwd = pwd + num
            
            # Adjust length
            if len(pwd) > length:
                pwd = pwd[:length]
            while len(pwd) < length:
                choice = secrets.choice((string.ascii_letters, string.digits, symbols))
                pwd += secrets.choice(choice)
            
            passwords.append(pwd)
        
        return passwords
    
    def generate_passwords_random(self, count, length, use_lower=True, use_upper=True, 
                                  use_digits=True, use_symbols=False, symbol_set="safe", 
                                  custom_symbols=""):
        """Generate random passwords using character sets"""
        if build_charset is None or generate_many is None:
            self.log("Error: PasswordGeneration module not available")
            return []
        
        # Determine symbol settings
        if symbol_set == "all":
            use_symbols_flag = True
            extra_symbols = ""
        elif symbol_set == "custom":
            use_symbols_flag = False
            extra_symbols = custom_symbols
        elif symbol_set == "safe":
            use_symbols_flag = False
            extra_symbols = "!@#$%&*()-_=+"
        else:
            use_symbols_flag = False
            extra_symbols = ""
        
        try:
            charset = build_charset(
                use_lower=use_lower,
                use_upper=use_upper,
                use_digits=use_digits,
                use_symbols=use_symbols_flag,
                extra_symbols=extra_symbols
            )
            return generate_many(count, length, charset)
        except Exception as e:
            self.log(f"Error generating passwords: {e}")
            return []
    
    def execute_task(self, task_data):
        """
        Execute a password testing task
        
        Args:
            task_data: Dictionary containing:
                - type: "test" or "generate_and_test"
                - target_url: URL to test (for test type)
                - username: Username to test (for test type)
                - passwords: List of passwords (for test type)
                - stop_after_first: Boolean (optional)
                - generation: Generation config (for generate_and_test type)
                - testing: Testing config (for generate_and_test type)
        """
        task_type = task_data.get("type", "test")
        
        if task_type == "generate_and_test":
            self.log("Received generate-and-test task")
            
            # Generate passwords
            gen_config = task_data.get("generation", {})
            mode = gen_config.get("mode", "random")
            count = gen_config.get("count", 100)
            length = gen_config.get("length", 12)
            
            self.log(f"Generating {count} passwords ({mode} mode)...")
            
            if mode == "ai":
                passwords = self.generate_passwords_ai(
                    keywords=gen_config.get("keywords", []),
                    count=count,
                    length=length,
                    capitalize=gen_config.get("capitalize", True),
                    leet=gen_config.get("leet", True),
                    insert_symbols=gen_config.get("insert_symbols", True),
                    symbols=gen_config.get("symbols", "!@#$%&*()-_=+"),
                    append_numbers=gen_config.get("append_numbers", True)
                )
            else:
                passwords = self.generate_passwords_random(
                    count=count,
                    length=length,
                    use_lower=gen_config.get("use_lower", True),
                    use_upper=gen_config.get("use_upper", True),
                    use_digits=gen_config.get("use_digits", True),
                    use_symbols=gen_config.get("use_symbols", False),
                    symbol_set=gen_config.get("symbol_set", "safe"),
                    custom_symbols=gen_config.get("custom_symbols", "")
                )
            
            self.log(f"Generated {len(passwords)} passwords")
            
            # Save passwords to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            passwords_file = Path(__file__).resolve().parent / f"generated_passwords_{timestamp}.txt"
            try:
                with open(passwords_file, 'w', encoding='utf-8') as f:
                    for pwd in passwords:
                        f.write(pwd + '\n')
                self.log(f"Saved passwords to: {passwords_file.name}")
            except Exception as e:
                self.log(f"Error saving passwords: {e}")
            
            # Now test them
            test_config = task_data.get("testing", {})
            target_url = test_config.get("target_url")
            username = test_config.get("username")
            stop_after_first = test_config.get("stop_after_first", True)
            
            self.log(f"Testing passwords for {username}@{target_url}")
            
        else:
            # Regular testing task
            target_url = task_data.get("target_url")
            username = task_data.get("username")
            passwords = task_data.get("passwords", [])
            stop_after_first = task_data.get("stop_after_first", True)
            
            self.log(f"Executing task: Testing {len(passwords)} passwords for {username}@{target_url}")
        
        # Create password tester and run
        tester = PasswordTester(
            target_url=target_url,
            username=username,
            passwords=passwords,
            stop_after_first=stop_after_first
        )
        
        results = tester.run_tests()
        
        self.log(f"Task completed: {results['total_succeeded']}/{results['total_tested']} succeeded")
        
        # Send results back to server
        self.send_log_report(results)
        
        return results
        
    def listen_for_tasks(self):
        """Listen for tasks from server"""
        self.log("Listening for tasks from server...")
        
        try:
            while self.connected:
                data = self.recv_json()
                if not data:
                    self.log("Connection lost to server")
                    self.connected = False
                    break
                    
                msg_type = data.get("type")
                
                if msg_type == "task":
                    task_data = data.get("data", {})
                    self.log("Received task from server")
                    self.execute_task(task_data)
                    
                elif msg_type == "ping":
                    # Respond to ping
                    self.send_json({"type": "pong"})
                    
                else:
                    self.log(f"Received message: {data}")
                    
        except KeyboardInterrupt:
            self.log("Client interrupted by user")
        except Exception as e:
            self.log(f"Error in listen loop: {e}")
        finally:
            self.disconnect()
            
    def disconnect(self):
        """Disconnect from server"""
        if self.connected:
            try:
                self.send_json({"type": "disconnect"})
            except:
                pass
            self.connected = False
            
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.log("Disconnected from server")
            
    def run(self):
        """Main client loop"""
        if not self.connect():
            return False
            
        # Send ready status
        self.send_ready()
        
        # Listen for tasks
        self.listen_for_tasks()
        
        return True


def main():
    """Main entry point for the client"""
    os.system('clear' if os.name == 'posix' else 'cls')
    print("\n" + "╔" + "═"*78 + "╗")
    print("║" + " "*20 + "DISTRIBUTED PASSWORD TESTING CLIENT" + " "*23 + "║")
    print("╚" + "═"*78 + "╝\n")
    
    # Get server details
    print("📡 Server Connection Settings:")
    server_host = input("   Server IP address [127.0.0.1]: ").strip() or "127.0.0.1"
    server_port = input("   Server port [5051]: ").strip() or "5051"
    client_name = input("   Client name [auto]: ").strip() or None
    
    try:
        server_port = int(server_port)
    except ValueError:
        print("\n❌ Invalid port number!")
        return
    
    print("\n" + "─"*80)
    print("🚀 Starting client...")
    print(f"   • Server: \033[1;32m{server_host}:{server_port}\033[0m")
    print(f"   • Client Name: \033[1;32m{client_name or 'auto-generated'}\033[0m")
    print("   • Press \033[1;31mCtrl+C\033[0m to stop the client")
    print("─"*80 + "\n")
    
    client = DistributedTestClient(server_host, server_port, client_name)
    client.run()


if __name__ == "__main__":
    main()
