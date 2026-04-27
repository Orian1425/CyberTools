import math

def snells_law(n1, theta1_deg, n2):
    theta1_rad = math.radians(theta1_deg)
    sin_theta2 = n1 * math.sin(theta1_rad) / n2
    if n1 > n2:
        critical_ang = math.asin(n2 / n1)
        if theta1_rad > critical_ang:
            return None
    theta2_rad = math.asin(sin_theta2)
    return math.degrees(theta2_rad)

class SnellsLawSimulation:
    def __init__(self, canvas):
        self.canvas = canvas

    def draw_scene(self, theta1, n1, n2):
        self.canvas.delete("all")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if width <= 1: width = 800
        if height <= 1: height = 600

        center_x = width // 2
        center_y = height // 2

        # Draw mediums
        if n1 < n2:
            self.canvas.create_rectangle(0, 0, width, center_y, fill="white", outline="")
            self.canvas.create_rectangle(0, center_y, width, height, fill="#add8e6", outline="") # Light blue
        else:
            self.canvas.create_rectangle(0, 0, width, center_y, fill="#add8e6", outline="") # Light blue
            self.canvas.create_rectangle(0, center_y, width, height, fill="white", outline="")
            
        # Draw normal axis (dashed)
        self.canvas.create_line(center_x, 0, center_x, height, fill="gray", dash=(4, 4))
        # Draw boundary
        self.canvas.create_line(0, center_y, width, center_y, fill="black", width=2)

        # Calculate refraction
        theta2 = snells_law(n1, theta1, n2)
        ray_length = min(width, height) * 0.4

        # Incident ray
        hitray_end_x = center_x - ray_length * math.sin(math.radians(theta1))
        hitray_end_y = center_y - ray_length * math.cos(math.radians(theta1))
        self.canvas.create_line(hitray_end_x, hitray_end_y, center_x, center_y, fill="red", width=3)

        reflected = False
        if theta2 is not None:
            # Refracted ray
            breakray_end_x = center_x + ray_length * math.sin(math.radians(theta2))
            breakray_end_y = center_y + ray_length * math.cos(math.radians(theta2))
            self.canvas.create_line(center_x, center_y, breakray_end_x, breakray_end_y, fill="red", width=3)
        else:
            # Total internal reflection
            reflected = True
            breakray_end_x = center_x + ray_length * math.sin(math.radians(theta1))
            breakray_end_y = center_y - ray_length * math.cos(math.radians(theta1))
            self.canvas.create_line(center_x, center_y, breakray_end_x, breakray_end_y, fill="red", width=3)

        # Add text labels
        self.canvas.create_text(20, 20, text=f"Angle: {theta1:.1f}°", anchor="w", fill="black", font=("Arial", 14, "bold"))
        if reflected:
            self.canvas.create_text(20, 50, text=f"Reflection: {theta1:.1f}°", anchor="w", fill="black", font=("Arial", 14, "bold"))
            self.canvas.create_text(20, 80, text="TOTAL INTERNAL REFLECTION", anchor="w", fill="red", font=("Arial", 12, "bold"))
        else:
            self.canvas.create_text(20, 50, text=f"Refraction: {theta2:.1f}°", anchor="w", fill="black", font=("Arial", 14, "bold"))
        
        self.canvas.create_text(20, 110 if reflected else 80, text=f"n1: {n1}", anchor="w", fill="black", font=("Arial", 14))
        self.canvas.create_text(20, 140 if reflected else 110, text=f"n2: {n2}", anchor="w", fill="black", font=("Arial", 14))
