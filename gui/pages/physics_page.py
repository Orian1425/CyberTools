import customtkinter as ctk
from tools.Physics.collision_sim import PhysicsSimulation

class PhysicsPage(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.simulation = None

        # --- Layout: Left Panel (Settings) ---
        self.settings_frame = ctk.CTkFrame(self, width=250)
        self.settings_frame.pack(side="left", fill="y", padx=10, pady=10)
        self.settings_frame.pack_propagate(False) # Keep width fixed

        self.title_label = ctk.CTkLabel(self.settings_frame, text="Physics Settings", font=("Roboto", 20, "bold"))
        self.title_label.pack(pady=(10, 20))

        # Number of balls selection
        self.top_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        self.top_frame.pack(pady=5, padx=10, fill="x")

        self.ball_amount_label = ctk.CTkLabel(self.top_frame, text="Balls:")
        self.ball_amount_label.pack(side="left")

        self.ball_amount_var = ctk.StringVar(value="2")
        self.ball_amount_menu = ctk.CTkOptionMenu(
            self.top_frame, 
            values=["2", "3", "4", "5"],
            variable=self.ball_amount_var,
            command=self.update_ball_inputs,
            width=80
        )
        self.ball_amount_menu.pack(side="right")

        # Scrollable frame for dynamic inputs
        self.inputs_frame = ctk.CTkScrollableFrame(self.settings_frame)
        self.inputs_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Start button - always visible at the bottom of settings
        self.start_btn = ctk.CTkButton(self.settings_frame, text="Start Simulation", font=("Roboto", 16, "bold"), command=self.start_sim)
        self.start_btn.pack(pady=10, padx=10, fill="x")

        # --- Layout: Right Panel (Simulation Canvas) ---
        self.canvas_frame = ctk.CTkFrame(self)
        self.canvas_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # We use standard tk.Canvas since ctk doesn't have a native Canvas
        # but we style it to look integrated
        import tkinter as tk
        self.canvas = tk.Canvas(self.canvas_frame, bg="white", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=2, pady=2)

        # Initialize the inputs
        self.ball_entries = []
        self.update_ball_inputs("2")

        # Handle page destruction to stop loop
        self.bind("<Destroy>", self.on_destroy)

    def update_ball_inputs(self, choice):
        # Clear existing inputs
        for widget in self.inputs_frame.winfo_children():
            widget.destroy()
        
        self.ball_entries.clear()
        
        num_balls = int(choice)
        
        for i in range(num_balls):
            frame = ctk.CTkFrame(self.inputs_frame)
            frame.pack(pady=5, fill="x", padx=5)
            
            lbl = ctk.CTkLabel(frame, text=f"Ball {i+1}", font=("Roboto", 14, "bold"))
            lbl.pack(anchor="w", padx=5, pady=(5, 0))
            
            # Mass
            m_frame = ctk.CTkFrame(frame, fg_color="transparent")
            m_frame.pack(fill="x", padx=5, pady=2)
            ctk.CTkLabel(m_frame, text="Mass:").pack(side="left")
            m_entry = ctk.CTkEntry(m_frame, width=50)
            m_entry.insert(0, "10")
            m_entry.pack(side="right")
            
            # Vx
            vx_frame = ctk.CTkFrame(frame, fg_color="transparent")
            vx_frame.pack(fill="x", padx=5, pady=2)
            ctk.CTkLabel(vx_frame, text="Vx:").pack(side="left")
            vx_entry = ctk.CTkEntry(vx_frame, width=50)
            vx_entry.insert(0, "2")
            vx_entry.pack(side="right")
            
            # Vy
            vy_frame = ctk.CTkFrame(frame, fg_color="transparent")
            vy_frame.pack(fill="x", padx=5, pady=2)
            ctk.CTkLabel(vy_frame, text="Vy:").pack(side="left")
            vy_entry = ctk.CTkEntry(vy_frame, width=50)
            vy_entry.insert(0, "0")
            vy_entry.pack(side="right")
            
            self.ball_entries.append({
                "m": m_entry,
                "vx": vx_entry,
                "vy": vy_entry
            })

    def start_sim(self):
        ball_amount = int(self.ball_amount_var.get())
        masses = []
        vxs = []
        vys = []
        
        try:
            for entry in self.ball_entries:
                masses.append(float(entry["m"].get()))
                vxs.append(float(entry["vx"].get()))
                vys.append(float(entry["vy"].get()))
                
            # Stop existing simulation if any
            if self.simulation:
                self.simulation.stop()

            # Wait for canvas layout to update if it's the first time
            self.canvas.update_idletasks()
                
            # Start new simulation
            self.simulation = PhysicsSimulation(self.canvas, ball_amount, masses, vxs, vys)
            self.simulation.start()
        except ValueError:
            print("Please enter valid numbers for all fields.")

    def on_destroy(self, event):
        if self.simulation:
            self.simulation.stop()
