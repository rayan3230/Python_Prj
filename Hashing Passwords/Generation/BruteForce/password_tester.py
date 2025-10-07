"""
Headless password tester module (non-GUI version)
Can be imported and used programmatically by the client script
"""

import requests
import time
import os
from datetime import datetime


class PasswordTester:
    def __init__(self, target_url, username, passwords, stop_after_first=True, debug=False):
        """
        Initialize the password tester
        
        Args:
            target_url: The login URL to test against
            username: The username to test with
            passwords: List of passwords to test
            stop_after_first: Stop after first successful password
            debug: Enable debug output (shows response URLs and snippets)
        """
        self.target_url = target_url
        self.username = username
        self.passwords = passwords
        self.stop_after_first = stop_after_first
        self.debug = debug
        self.session = requests.Session()
        self.results = []
        self.log_messages = []
        
    def log(self, message):
        """Add a log message"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {message}"
        self.log_messages.append(log_entry)
        print(log_entry)
        
    def test_password(self, password):
        """
        Test a single password
        
        Returns:
            dict: Result containing success, password, time_taken, note
        """
        start = time.time()
        try:
            resp = self.session.post(
                self.target_url, 
                data={"username": self.username, "password": password}, 
                allow_redirects=True, 
                timeout=10
            )
        except Exception as e:
            took = time.time() - start
            return {
                "success": False,
                "password": password,
                "time_taken": took,
                "note": f"ERROR: {e}",
                "timestamp": datetime.now().isoformat()
            }
        
        took = time.time() - start
        success = False
        
        try:
            final_url = resp.url or ""
            status_code = resp.status_code
            
            # Debug output
            if self.debug:
                self.log(f"DEBUG - Status: {status_code}, Final URL: {final_url}")
                self.log(f"DEBUG - Response snippet: {resp.text[:200]}...")
            
            # Check if redirected to dashboard (successful login)
            if "/dashboard" in final_url:
                success = True
            # Also check for successful status code and no error messages
            elif status_code == 200 and "Invalid" not in resp.text and "incorrect" not in resp.text.lower():
                # Some apps might not redirect but show success differently
                if "welcome" in resp.text.lower() or "success" in resp.text.lower():
                    success = True
        except Exception as e:
            success = False
            if self.debug:
                self.log(f"DEBUG - Exception checking response: {e}")
            
        result = {
            "success": success,
            "password": password,
            "time_taken": took,
            "note": "OK" if success else "FAIL",
            "timestamp": datetime.now().isoformat(),
            "final_url": final_url if 'final_url' in locals() else "",
            "status_code": status_code if 'status_code' in locals() else 0
        }
        
        return result
        
    def run_tests(self):
        """
        Run all password tests
        
        Returns:
            dict: Summary with results, logs, and statistics
        """
        total = len(self.passwords)
        succeeded = 0
        
        self.log(f"Starting password test for user: {self.username}")
        self.log(f"Target URL: {self.target_url}")
        self.log(f"Total passwords to test: {total}")
        
        for idx, pw in enumerate(self.passwords, start=1):
            result = self.test_password(pw)
            self.results.append(result)
            
            status = "SUCCESS" if result["success"] else "FAIL"
            if result["note"].startswith("ERROR"):
                status = "ERROR"
                
            self.log(f"{idx}/{total} - {status} - {pw} ({result['time_taken']:.2f}s)")
            
            if result["success"]:
                succeeded += 1
                if self.stop_after_first:
                    self.log("Found successful password! Stopping as requested.")
                    break
                    
            # Small delay to be polite to the server
            time.sleep(0.1)
            
        self.log(f"Finished. {succeeded} succeeded out of {idx} tried.")
        
        return {
            "username": self.username,
            "target_url": self.target_url,
            "total_tested": idx,
            "total_succeeded": succeeded,
            "results": self.results,
            "logs": self.log_messages,
            "timestamp": datetime.now().isoformat()
        }
        
    def save_results_to_file(self, output_path):
        """Save results to a tab-separated file"""
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write("timestamp\tusername\tpassword\tsuccess\tnote\ttime_taken\n")
                for result in self.results:
                    f.write(
                        f"{result['timestamp']}\t{self.username}\t{result['password']}\t"
                        f"{int(result['success'])}\t{result['note']}\t{result['time_taken']:.3f}\n"
                    )
            self.log(f"Results saved to: {output_path}")
            return True
        except Exception as e:
            self.log(f"Error saving results: {e}")
            return False


def run_test_from_config(target_url, username, passwords, stop_after_first=True):
    """
    Convenience function to run a test and return results
    
    Args:
        target_url: The login URL to test
        username: Username to test with
        passwords: List of passwords to test
        stop_after_first: Stop after first success
        
    Returns:
        dict: Test results and logs
    """
    tester = PasswordTester(target_url, username, passwords, stop_after_first)
    return tester.run_tests()
