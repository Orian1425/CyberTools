# gui/av_page.py
import os
import threading
import time
import config
import customtkinter as ctk
from tkinter import filedialog
from tools.Antivirus.antivirus import VirusTotalScanner # ייבוא ה-Class שיצרנו

class AVPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        # Scanner configuration
        self.api_key = config.VT_API_KEY
        self.scanner = VirusTotalScanner(self.api_key)

        # Title
        self.label = ctk.CTkLabel(self, text="VirusTotal Scanner", font=("Roboto", 24, "bold"))
        self.label.pack(pady=(10, 5))

        # Scanner Frame (directly in main frame now)
        self.scanner_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.scanner_frame.pack(pady=10)

        # Action Buttons
        self.file_btn = ctk.CTkButton(self.scanner_frame, text="Scan File", command=self.handle_file_scan)
        self.file_btn.grid(row=0, column=0, padx=10, pady=5)

        self.folder_btn = ctk.CTkButton(self.scanner_frame, text="Scan Folder", command=self.handle_folder_scan)
        self.folder_btn.grid(row=0, column=1, padx=10, pady=5)

        # Progress Bar
        self.progress = ctk.CTkProgressBar(self.scanner_frame, width=400)
        self.progress.set(0)
        self.progress.grid(row=1, column=0, columnspan=2, pady=20)

        # Log box
        self.log_label = ctk.CTkLabel(self, text="Activity Log", font=("Roboto", 16, "bold"))
        self.log_label.pack(pady=(5, 0))
        self.log_box = ctk.CTkTextbox(self, height=200)
        self.log_box.pack(pady=5, padx=20, fill="both", expand=True)

    def log(self, message):
        """Update the log box from the scanning thread"""
        if self.winfo_exists():
            self.log_box.insert("end", f"> {message}\n")
            self.log_box.see("end")

    def handle_file_scan(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.log(f"Starting scan for: {file_path}\n")
            self.progress.start()
            self.scanner.scan_file(file_path, self.on_scan_complete)

    def handle_folder_scan(self):
        folder_path = filedialog.askdirectory()
        if not folder_path:
            return

        all_files = self.get_all_files(folder_path)
        files_to_scan = all_files[:4] 
        
        if len(all_files) > 4:
            self.log(f"Note: Found {len(all_files)} files, but free API limits us to 4.\n")

        threading.Thread(target=self.process_queue, args=(files_to_scan,), daemon=True).start()

    def process_queue(self, file_list):
        self.progress.start()
        for file_path in file_list:
            self.log(f"Processing: {os.path.basename(file_path)}")
            scan_done = threading.Event()
            self.scanner.scan_file(file_path, self.on_scan_complete, scan_done)
            scan_done.wait()
        self.log("Folder scan task finished.\n")
        self.progress.stop()

    def get_all_files(self, path):
        file_list = []
        for root, dirs, files in os.walk(path):
            for file in files:
                file_list.append(os.path.join(root, file))
        return file_list
    
    def on_scan_complete(self, result):
        self.log(f"{result}\n")
        self.progress.stop()
        self.progress.set(1)
