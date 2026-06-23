# gui/pages/rdp_page.py
import os
import threading
import shutil
import subprocess
import customtkinter as ctk
from tkinter import filedialog, messagebox
import config
from tools.RDP.rdp_host import Host
from tools.RDP.rdp_client import Client

class RDPPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        # Title
        self.label = ctk.CTkLabel(self, text="Remote Desktop Protocol (RDP)", font=("Roboto", 24, "bold"))
        self.label.pack(pady=(10, 5))

        # Tabview
        self.tabview = ctk.CTkTabview(self, height=200)
        self.tabview.pack(pady=5, padx=20, fill="x")

        self.tab_host = self.tabview.add("RDP Host (Server)")
        self.tab_client = self.tabview.add("RDP Client")

        # Setup Tabs
        self._setup_host_tab()
        self._setup_client_tab()

        # Progress / Compile Status
        self.progress = ctk.CTkProgressBar(self, width=400)
        self.progress.set(0)
        self.progress.pack(pady=10)

        # Log box
        self.log_label = ctk.CTkLabel(self, text="Activity Log", font=("Roboto", 16, "bold"))
        self.log_label.pack(pady=(5, 0))
        self.log_box = ctk.CTkTextbox(self, height=180)
        self.log_box.pack(pady=5, padx=20, fill="both", expand=True)

        # Host state
        self.host_instance = None
        self.host_thread = None
        self.broadcast_thread = None
        self.broadcast_stop_event = threading.Event()

        # Client state
        self.client_instance = None
        self.client_thread = None

    def log(self, msg):
        if self.winfo_exists():
            self.log_box.insert("end", f"> {msg}\n")
            self.log_box.see("end")

    def _setup_host_tab(self):
        frame = ctk.CTkFrame(self.tab_host, fg_color="transparent")
        frame.pack(pady=15)

        self.host_start_btn = ctk.CTkButton(
            frame, 
            text="Start Host Server", 
            fg_color="green", 
            hover_color="darkgreen", 
            text_color="white",
            command=self.start_host
        )
        self.host_start_btn.pack(side="left", padx=10)

        self.host_stop_btn = ctk.CTkButton(
            frame, 
            text="Stop Host Server", 
            fg_color="red", 
            hover_color="darkred", 
            text_color="white",
            state="disabled", 
            command=self.stop_host
        )
        self.host_stop_btn.pack(side="left", padx=10)

    def _setup_client_tab(self):
        frame = ctk.CTkFrame(self.tab_client, fg_color="transparent")
        frame.pack(pady=15)

        self.client_start_btn = ctk.CTkButton(
            frame, 
            text="Start Client Connection", 
            fg_color="green", 
            hover_color="darkgreen", 
            text_color="white",
            command=self.start_client
        )
        self.client_start_btn.pack(side="left", padx=10)

        self.client_stop_btn = ctk.CTkButton(
            frame, 
            text="Stop Client Connection", 
            fg_color="red", 
            hover_color="darkred", 
            text_color="white",
            state="disabled", 
            command=self.stop_client
        )
        self.client_stop_btn.pack(side="left", padx=10)

        self.client_exe_btn = ctk.CTkButton(
            frame, 
            text="Download Client EXE", 
            fg_color="#9b59b6", 
            hover_color="#8e44ad", 
            text_color="white",
            command=self.download_client_exe
        )
        self.client_exe_btn.pack(side="left", padx=10)

    def start_host(self):
        self.log("Starting RDP Host Server...")
        self.host_start_btn.configure(state="disabled")
        self.host_stop_btn.configure(state="normal")

        rdp_port = config.PORTS["RDP"]
        broadcast_port = config.PORTS["Broadcast"]
        
        self.host_instance = Host("0.0.0.0", rdp_port, shutdown_callback=self.stop_host_from_keypress, log_callback=self.log)
        
        # 1. Start broadcast presence   
        self.broadcast_stop_event.clear() 
        self.broadcast_thread = threading.Thread(
            target=Host.broadcast_presence,
            args=(self.broadcast_stop_event, broadcast_port,self.log),
            daemon=True
        )
        self.broadcast_thread.start()
        self.log(f"Broadcasting server presence on port {broadcast_port}...")

        # 2. Start Host listener
        
        def run_host():
            self.log(f"Listening for RDP Client connection on port {rdp_port}...")
            success = self.host_instance.start()
            if success:
                self.log("Host session ended gracefully.")
            else:
                self.log("Host listening failed or was canceled.")
            self.after(0, self.reset_host_ui_state)

        self.host_thread = threading.Thread(target=run_host, daemon=True)
        self.host_thread.start()

    def stop_host_from_keypress(self):
        self.log("Session stopped via Ctrl+Esc keyboard shortcut.")
        self.after(0, self.stop_host)

    def stop_host(self):
        self.log("Stopping RDP Host Server...")
        self.broadcast_stop_event.set()
        if self.host_instance:
            self.host_instance.stop()
            self.host_instance = None
        self.reset_host_ui_state()

    def reset_host_ui_state(self):
        if self.winfo_exists():
            self.host_start_btn.configure(state="normal")
            self.host_stop_btn.configure(state="disabled")

    def start_client(self):
        self.log("Starting RDP Client auto-discovery...")
        self.client_start_btn.configure(state="disabled")
        self.client_stop_btn.configure(state="normal")

        rdp_port = config.PORTS["RDP"]
        broadcast_port = config.PORTS["Broadcast"]

        def run_client():
            server_ip = Client.discover_server_ip(broadcast_port, timeout=5, log_callback=self.log)
            if not server_ip:
                self.log("Error: Could not discover any RDP Host Server on the LAN.")
                self.after(0, self.stop_client)
                return

            self.log(f"Discovered Host Server IP: {server_ip}. Connecting on port {rdp_port}...")
            try:
                self.client_instance = Client(server_ip, rdp_port, log_callback=self.log)
                self.log("Connected to Host. Streaming screen recording...")
                self.client_instance.is_running = True
                
                # Start screen recorder
                self.client_instance.start_screen_record()
                # Run command reception loop (blocking)
                self.client_instance.get_commands()
            except Exception as e:
                self.log(f"Client connection failed: {e}")
            finally:
                self.after(0, self.stop_client)

        self.client_thread = threading.Thread(target=run_client, daemon=True)
        self.client_thread.start()

    def stop_client(self):
        self.log("Stopping RDP Client Connection...")
        if self.client_instance:
            self.client_instance.stop()
            self.client_instance = None
        if self.winfo_exists():
            self.client_start_btn.configure(state="normal")
            self.client_stop_btn.configure(state="disabled")
            self.log("RDP Client Connection stopped.")

    def download_client_exe(self):
        dest_path = filedialog.asksaveasfilename(
            defaultextension=".exe",
            filetypes=[("Executable Files", "*.exe")],
            initialfile="rdp_client.exe",
            title="Download RDP Client Executable"
        )
        if not dest_path:
            return

        self.client_exe_btn.configure(state="disabled")
        self.progress.start()
        self.log("Initializing client executable compilation...")

        def compile_thread():
            try:
                # Resolve paths relative to config.BASE_DIR
                pip_path = os.path.join(config.BASE_DIR, "cyberToolsEnv", "Scripts", "pip.exe")
                pyinstaller_path = os.path.join(config.BASE_DIR, "cyberToolsEnv", "Scripts", "pyinstaller.exe")
                
                # Install PyInstaller if missing
                if not os.path.exists(pyinstaller_path):
                    self.log("PyInstaller not found. Installing into virtual environment...")
                    subprocess.run(
                        [pip_path, "install", "pyinstaller"],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    self.log("PyInstaller installed successfully.")

                self.log("Compiling client script using PyInstaller (onefile, no-console)...")
                client_script_path = os.path.join(config.BASE_DIR, "tools", "RDP", "rdp_client.py")
                
                # Compile using PyInstaller
                cmd = [
                    pyinstaller_path,
                    "--onefile",
                    "--noconsole",
                    "--clean",
                    "--workpath", os.path.join(config.BASE_DIR, "build"),
                    "--distpath", os.path.join(config.BASE_DIR, "dist"),
                    "--specpath", config.BASE_DIR,
                    client_script_path
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    self.log(f"Compilation error details:\n{result.stderr}")
                    messagebox.showerror("Build Failed", f"PyInstaller compilation failed:\n{result.stderr}")
                    return

                compiled_exe = os.path.join(config.BASE_DIR, "dist", "rdp_client.exe")
                if os.path.exists(compiled_exe):
                    shutil.copy2(compiled_exe, dest_path)
                    self.log(f"Success! Client executable saved to: {dest_path}")
                    messagebox.showinfo("Success", f"Client executable successfully saved to:\n{dest_path}")
                else:
                    self.log("Error: Compiled output binary was not found in 'dist' directory.")
                    messagebox.showerror("Error", "Compiled client output binary could not be found.")

                # Cleanup build artifacts
                self.log("Cleaning up workspace build folders...")
                for path in [
                    os.path.join(config.BASE_DIR, "build"),
                    os.path.join(config.BASE_DIR, "dist"),
                    os.path.join(config.BASE_DIR, "rdp_client.spec")
                ]:
                    if os.path.exists(path):
                        if os.path.isdir(path):
                            shutil.rmtree(path)
                        else:
                            os.remove(path)
                self.log("Cleanup complete.")

            except Exception as e:
                self.log(f"Failed to generate EXE: {e}")
                messagebox.showerror("Error", f"An error occurred during build:\n{e}")
            finally:
                if self.winfo_exists():
                    self.progress.stop()
                    self.progress.set(0)
                    self.client_exe_btn.configure(state="normal")

        threading.Thread(target=compile_thread, daemon=True).start()

    def destroy(self):
        self.stop_host()
        self.stop_client()
        super().destroy()
