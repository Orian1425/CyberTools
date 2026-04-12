import customtkinter as ctk

# הגדרת מראה האפליקציה (כהה מתאים לסייבר!)
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class CyberApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # הגדרות חלון
        self.title("Cyber Tools")
        self.geometry("600x400")

        # יצירת כותרת
        self.label = ctk.CTkLabel(self, text="Cyber Security Tools", font=("Roboto", 24))
        self.label.pack(pady=20)

        # כפתור לדוגמה להפעלת סקריפט
        self.scan_button = ctk.CTkButton(self, text="Run Port Scanner", command=self.run_tool)
        self.scan_button.pack(pady=10)

        # תיבת טקסט להצגת פלט (Results)
        self.result_box = ctk.CTkTextbox(self, width=500, height=200)
        self.result_box.pack(pady=20)

    def run_tool(self):
        """פונקציה שתפעיל את הסקריפט שלך"""
        # כאן בעתיד נחבר את הסקריפט האמיתי
        self.result_box.insert("insert", "[+] Starting Scan on 127.0.0.1...\n")
        self.result_box.insert("insert", "[+] Port 80: OPEN\n")

# הרצת האפליקציה
if __name__ == "__main__":
    app = CyberApp()
    app.mainloop()