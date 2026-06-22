# gui/ftp_page.py
import threading, os
import config
import customtkinter as ctk
from tkinter import filedialog
from tools.FTP.ftp_client import FTPClient
from tools.FTP.ftp_server import FTPServer

class FTPPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        # Title
        self.label = ctk.CTkLabel(self, text="FTP File Transfer Protocol", font=("Roboto", 24, "bold"))
        self.label.pack(pady=(10, 5))

        # Tabview
        self.tabview = ctk.CTkTabview(self, height=200)
        self.tabview.pack(pady=5, padx=20, fill="x")

        self.tab_client = self.tabview.add("FTP Client")
        self.tab_server = self.tabview.add("FTP Server")

        # Setup Tabs
        self._setup_client_tab()
        self._setup_server_tab()

        # Log box
        self.log_label = ctk.CTkLabel(self, text="Activity Log", font=("Roboto", 16, "bold"))
        self.log_label.pack(pady=(5, 0))
        self.log_box = ctk.CTkTextbox(self, height=200)
        self.log_box.pack(pady=5, padx=20, fill="both", expand=True)

        # Server threading
        self.server_stop_event = threading.Event()
        self.server_thread = None

    def _setup_client_tab(self):
        frame = ctk.CTkFrame(self.tab_client, fg_color="transparent")
        frame.pack(pady=10)

        # Upload Section
        self.upload_btn = ctk.CTkButton(frame, text="Upload File", command=self.handle_upload)
        self.upload_btn.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        # Download Section
        self.filename_entry = ctk.CTkEntry(frame, placeholder_text="Enter filename to download...", width=250)
        self.filename_entry.grid(row=1, column=0, padx=10, pady=5)
        
        self.download_btn = ctk.CTkButton(frame, text="Download File", fg_color="green", hover_color="darkgreen", command=self.handle_download)
        self.download_btn.grid(row=1, column=1, padx=10, pady=5)

    def _setup_server_tab(self):
        frame = ctk.CTkFrame(self.tab_server, fg_color="transparent")
        frame.pack(pady=10)

        self.server_start_btn = ctk.CTkButton(frame, text="Start Server", fg_color="green", hover_color="darkgreen", command=self.start_server)
        self.server_start_btn.pack(side="left", padx=10)

        self.server_stop_btn = ctk.CTkButton(frame, text="Stop Server", fg_color="red", hover_color="darkred", state="disabled", command=self.stop_server)
        self.server_stop_btn.pack(side="left", padx=10)

    def start_server(self):
        self.server_stop_event.clear()
        self.server_start_btn.configure(state="disabled")
        self.server_stop_btn.configure(state="normal")
        
        # Pass self.log to the constructor as required
        server_instance = FTPServer(self.log, config.SERVER_IP, config.PORTS["FTP"])
        
        self.server_thread = threading.Thread(
            target=server_instance.start_accepting,
            args=(self.server_stop_event,),
            daemon=True
        )
        self.server_thread.start()


    def stop_server(self):
        self.log("Stopping FTP Server...")
        self.server_stop_event.set()
        self.server_start_btn.configure(state="normal")
        self.server_stop_btn.configure(state="disabled")

    def destroy(self):
        self.server_stop_event.set()
        super().destroy()

    def log(self, msg):
        if self.winfo_exists():
            self.log_box.insert("end", f"> {msg}\n")
            self.log_box.see("end")

    def handle_upload(self):
        path = filedialog.askopenfilename()
        if path:
            filename = os.path.basename(path)
            self.log(f"Initiating upload: {filename}")
            
            def run_upload():
                client = FTPClient(config.PORTS["FTP"], config.PORTS["Broadcast"])
                if client.is_connected:
                    status = client.upload_file_to_server(path)
                    self.log(f"Upload Status: {status}")
                else:
                    self.log(f"Upload Status: SERVER_DOWN ({client.error_message})")

            threading.Thread(target=run_upload, daemon=True).start()

    def handle_download(self):
        filename = self.filename_entry.get()
        if filename:
            self.log(f"Initiating download: {filename}")
            
            def run_download():
                client = FTPClient(config.PORTS["FTP"], config.PORTS["Broadcast"])
                if client.is_connected:
                    status = client.download_file_to_client(filename)
                    self.log(f"Download Status: {status}")
                else:
                    self.log(f"Download Status: SERVER_DOWN ({client.error_message})")

            threading.Thread(target=run_download, daemon=True).start()
        else:
            self.log("Download Error: NO_FILE_SELECTED")


       