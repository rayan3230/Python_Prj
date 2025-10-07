"""
Distributed Password Testing - Client
Connects to server, receives tasks, runs password tests, and sends logs back
"""

import socket
import json
import os
from datetime import datetime
from password_tester import PasswordTester


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
        
    def execute_task(self, task_data):
        """
        Execute a password testing task
        
        Args:
            task_data: Dictionary containing:
                - target_url: URL to test
                - username: Username to test
                - passwords: List of passwords
                - stop_after_first: Boolean (optional)
        """
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
    print("="*80)
    print("DISTRIBUTED PASSWORD TESTING CLIENT")
    print("="*80)
    
    # Get server details
    server_host = input("Enter server IP address [127.0.0.1]: ").strip() or "127.0.0.1"
    server_port = input("Enter server port [5051]: ").strip() or "5051"
    client_name = input("Enter client name [auto]: ").strip() or None
    
    try:
        server_port = int(server_port)
    except ValueError:
        print("Invalid port number!")
        return
        
    print("\nStarting client...")
    print(f"Server: {server_host}:{server_port}")
    print(f"Client Name: {client_name or 'auto-generated'}")
    print("\nPress Ctrl+C to stop the client\n")
    
    client = DistributedTestClient(server_host, server_port, client_name)
    client.run()


if __name__ == "__main__":
    main()
