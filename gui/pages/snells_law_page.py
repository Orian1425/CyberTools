import customtkinter as ctk
import tkinter as tk
from tools.Physics.snells_law_sim import SnellsLawSimulation

class SnellsLawPage(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # --- Layout: Left Panel (Settings) ---
        self.settings_frame = ctk.CTkFrame(self, width=250)
        self.settings_frame.pack(side="left", fill="y", padx=10, pady=10)
        self.settings_frame.pack_propagate(False)

        self.title_label = ctk.CTkLabel(self.settings_frame, text="Snell's Law", font=("Roboto", 20, "bold"))
        self.title_label.pack(pady=(10, 20))

        # Refractive Index n1
        n1_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        n1_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(n1_frame, text="Medium 1 (n1):").pack(side="left")
        self.n1_entry = ctk.CTkEntry(n1_frame, width=60)
        self.n1_entry.insert(0, "1.0") # Default Air
        self.n1_entry.pack(side="right")

        # Refractive Index n2
        n2_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        n2_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(n2_frame, text="Medium 2 (n2):").pack(side="left")
        self.n2_entry = ctk.CTkEntry(n2_frame, width=60)
        self.n2_entry.insert(0, "1.5") # Default Glass
        self.n2_entry.pack(side="right")

        # Update button for indices
        self.update_btn = ctk.CTkButton(self.settings_frame, text="Update Mediums", command=self.draw_simulation)
        self.update_btn.pack(pady=10, padx=10, fill="x")

        # Angle Slider
        self.angle_label = ctk.CTkLabel(self.settings_frame, text="Incident Angle: 30°")
        self.angle_label.pack(pady=(20, 5))

        self.angle_slider = ctk.CTkSlider(
            self.settings_frame, 
            from_=0, 
            to=89.9, 
            command=self.on_slider_change
        )
        self.angle_slider.set(30)
        self.angle_slider.pack(padx=10, fill="x")

        # --- Layout: Right Panel (Simulation Canvas) ---
        self.canvas_frame = ctk.CTkFrame(self)
        self.canvas_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(self.canvas_frame, bg="white", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=2, pady=2)

        self.simulation = SnellsLawSimulation(self.canvas)

        # Bind resize to redraw
        self.canvas.bind("<Configure>", lambda e: self.draw_simulation())

        # Initial Draw
        self.after(100, self.draw_simulation) # short delay to let layout compute

    def on_slider_change(self, value):
        self.angle_label.configure(text=f"Incident Angle: {value:.1f}°")
        self.draw_simulation()

    def draw_simulation(self):
        try:
            n1 = float(self.n1_entry.get())
            n2 = float(self.n2_entry.get())
            theta1 = self.angle_slider.get()
            
            # Ensure safe values
            n1 = max(0.1, n1)
            n2 = max(0.1, n2)

            self.simulation.draw_scene(theta1, n1, n2)
        except ValueError:
            # Silently fail if they type something invalid temporarily
            pass
