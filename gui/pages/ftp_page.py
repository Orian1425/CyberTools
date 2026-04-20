# gui/ftp_page.py
import config
import customtkinter as ctk
from tkinter import filedialog
from tools.FTP.ftp_client import FTPClient

class FTPPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        # כותרת העמוד
        self.label = ctk.CTkLabel(self, text="FTP File Transfer Protocol", font=("Roboto", 24, "bold"))
        self.label.pack(pady=20)

        # כפתור העלאה
        self.upload_btn = ctk.CTkButton(self, text="Upload File", command=self.handle_upload)
        self.upload_btn.pack(pady=10)

        # שדה להורדה
        self.filename_entry = ctk.CTkEntry(self, placeholder_text="Enter filename to download...", width=250)
        self.filename_entry.pack(pady=10)
        
        self.download_btn = ctk.CTkButton(self, text="Download File", fg_color="green", command=self.handle_download)
        self.download_btn.pack(pady=10)

        # לוגים
        self.log_box = ctk.CTkTextbox(self, width=450, height=150)
        self.log_box.pack(pady=20)

    def log(self, msg):
        self.log_box.insert("end", f"> {msg}\n")
        self.log_box.see("end")

    def handle_upload(self):
        path = filedialog.askopenfilename()
        if path:
            client = FTPClient(config.HOST_IP, config.PORTS["FTP"])
            self.log(f"Upload Status: {client.upload_file_to_server(path) if client.is_connected else 'SERVER_DOWN'}")

    def handle_download(self):
        filename = self.filename_entry.get()
        if filename:
            client = FTPClient(config.HOST_IP, config.DEFAULT_PORT)
            self.log(f"Download Status: {client.download_file_to_client(filename) if client.is_connected else 'SERVER_DOWN'}")
        else:
            self.log(f"Download Status: NO_FILE_SELECTED")
       