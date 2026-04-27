import customtkinter as ctk

class PhysicsHubPage(ctk.CTkFrame):
    def __init__(self, master, navigate_callback, **kwargs):
        super().__init__(master, **kwargs)

        self.title_label = ctk.CTkLabel(self, text="Physics Simulators Hub", font=("Roboto", 28, "bold"))
        self.title_label.pack(pady=40)

        self.subtitle_label = ctk.CTkLabel(self, text="Select a simulation to launch:", font=("Roboto", 16))
        self.subtitle_label.pack(pady=(0, 30))

        # Buttons frame to center them
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(expand=True)

        self.collision_btn = ctk.CTkButton(
            self.btn_frame, 
            text="Collision Simulator", 
            font=("Roboto", 20, "bold"),
            width=250,
            height=60,
            command=lambda: navigate_callback("PhysicsCollision")
        )
        self.collision_btn.pack(pady=15)

        self.snells_btn = ctk.CTkButton(
            self.btn_frame, 
            text="Snell's Law Simulator", 
            font=("Roboto", 20, "bold"),
            width=250,
            height=60,
            command=lambda: navigate_callback("PhysicsSnell")
        )
        self.snells_btn.pack(pady=15)
