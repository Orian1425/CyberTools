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
        
        # הגדרת סורק (מומלץ להעביר את המפתח כמשתנה סביבה)
        self.api_key = config.VT_API_KEY
        self.scanner = VirusTotalScanner(self.api_key)

        # כותרת
        self.label = ctk.CTkLabel(self, text="VirusTotal Scanner", font=("Roboto", 24, "bold"))
        self.label.pack(pady=20)

        # כפתורי בחירה
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(pady=10)

        self.file_btn = ctk.CTkButton(self.btn_frame, text="Scan File", command=self.handle_file_scan)
        self.file_btn.grid(row=0, column=0, padx=10)

        self.folder_btn = ctk.CTkButton(self.btn_frame, text="Scan Folder", command=self.handle_folder_scan)
        self.folder_btn.grid(row=0, column=1, padx=10)

        # פס התקדמות (יופיע בזמן סריקה)
        self.progress = ctk.CTkProgressBar(self, width=400)
        self.progress.set(0)
        self.progress.pack(pady=20)

        # תיבת לוגים
        self.log_box = ctk.CTkTextbox(self, width=450, height=200)
        self.log_box.pack(pady=10, padx=20)

    def log(self, message):
        """פונקציה לעדכון תיבת הטקסט מה-Thread של הסריקה"""
        self.log_box.insert("end", f"> {message}\n")
        self.log_box.see("end")

    def handle_file_scan(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.log(f"Starting scan for: {file_path}")
            self.progress.start() # התחלת האנימציה של פס ההתקדמות
            
            # הרצת הסריקה עם Callback שיעדכן את הממשק בסיום
            self.scanner.scan_file(file_path, self.on_scan_complete)

    def handle_folder_scan(self):
        folder_path = filedialog.askdirectory()
        if not folder_path:
            return

        # 1. איסוף כל הקבצים
        all_files = self.get_all_files(folder_path)
        
        # 2. הגבלה ל-4 קבצים (בגלל מגבלת ה-API החינמי)
        files_to_scan = all_files[:4] 
        
        if len(all_files) > 4:
            self.log(f"Note: Found {len(all_files)} files, but free API limits us to 4.")

        # 3. הרצת הסריקה ב-Thread נפרד כדי לא לתקוע את ה-GUI
        threading.Thread(target=self.process_queue, args=(files_to_scan,), daemon=True).start()

    def process_queue(self, file_list):
        """עובר על הקבצים אחד אחד עם השהיה ביניהם"""
        self.progress.start()
        for file_path in file_list:
            self.log(f"Processing: {os.path.basename(file_path)}")
            scan_done = threading.Event()
            # אנחנו צריכים ש-scan_file יהיה סינכרוני במקרה הזה או להשתמש ב-Event
            # לצורך הפשטות, נפעיל את הסריקה ונחכה 15 שניות בין קובץ לקובץ (מגבלת ה-Rate Limit)
            self.scanner.scan_file(file_path, self.on_scan_complete, scan_done)
            scan_done.wait()
        self.log("Folder scan task finished.")
        self.progress.stop()

    def get_all_files(self, path):
        """פונקציית עזר שאוספת את כל הקבצים בתיקייה ובתתי-תיקיות"""
        file_list = []
        for root, dirs, files in os.walk(path):
            for file in files:
                file_list.append(os.path.join(root, file))
        return file_list
    
    def on_scan_complete(self, result):
        """פונקציה שנקראת כשהסריקה מסתיימת"""
        self.log(result)
        self.progress.stop()
        self.progress.set(1) # סימון סיום