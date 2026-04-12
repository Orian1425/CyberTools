import customtkinter as ctk
from gui.ftp_page import FTPPage

# הגדרת מראה האפליקציה (כהה מתאים לסייבר!)
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class CyberAppGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # הגדרות חלון
        self.title("Cyber Tools")
        self.geometry("700x500")

        # יצירת כותרת
        self.label = ctk.CTkLabel(self, text="Cyber Security Tools", font=("Roboto", 24))
        self.label.pack(pady=20)

        # יצירת קונטיינר ראשי שבו יתחלפו העמודים
        self.container = ctk.CTkFrame(self)
        self.container.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # תפריט צד (Sidebar)
        self.sidebar = ctk.CTkFrame(self, width=150)
        self.sidebar.pack(side="left", fill="y", padx=10, pady=10)

        self.menu_label = ctk.CTkLabel(self.sidebar, text="Menu", font=("Roboto", 20, "bold"))
        self.menu_label.pack(pady=20)

        # כפתור למעבר ל-FTP
        self.ftp_btn = ctk.CTkButton(self.sidebar, text="FTP Tool", command=self.show_ftp_page)
        self.ftp_btn.pack(pady=10, padx=10)

        # משתנה לשמירת העמוד הנוכחי
        self.current_page = None  
          
    def show_ftp_page(self):
        # הסרת העמוד הקודם אם קיים
        if self.current_page is not None:
            self.current_page.destroy()

        # הצגת עמוד ה-FTP בתוך הקונטיינר
        self.current_page = FTPPage(self.container)
        self.current_page.pack(fill="both", expand=True)