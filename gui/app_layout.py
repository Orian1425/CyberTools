import config
import customtkinter as ctk
from gui.pages.av_page import AVPage
from gui.pages.ftp_page import FTPPage
from gui.pages.settings_page import SettingsPage

# הגדרת מראה האפליקציה 
ctk.set_appearance_mode(config.APPEARANCE_MODE)
ctk.set_default_color_theme(config.DEFAULT_COLOR_THEME)

class CyberAppGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # הגדרות חלון
        self.title("Cyber Tools")
        self.geometry(config.WINDOW_SIZE)

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
        self.ftp_btn = ctk.CTkButton(self.sidebar, text="FTP Tool", command=lambda: self.show_page("FTP"))
        self.ftp_btn.pack(pady=10, padx=10)

        self.av_btn = ctk.CTkButton(self.sidebar, text="Anti-Virus", command=lambda: self.show_page("AV"))
        self.av_btn.pack(pady=10, padx=10)

        self.settings_btn = ctk.CTkButton(self.sidebar, text="Settings", command=lambda: self.show_page("Settings"), fg_color="gray")
        self.settings_btn.pack(side="bottom", pady=20, padx=10)

        # משתנה לשמירת העמוד הנוכחי
        self.current_page = None  
          
    def show_page(self, page_name):
        if self.current_page:
            self.current_page.destroy()

        if page_name == "FTP":
            self.current_page = FTPPage(self.container)
        elif page_name == "AV":
            self.current_page = AVPage(self.container)
        elif page_name == "Settings":
            self.current_page = SettingsPage(self.container)
        
        self.current_page.pack(fill="both", expand=True)