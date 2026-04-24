import math

class Ball:
    def __init__(self, x, y, m, radius, color, vy, vx, ax=0):
        self.x = x
        self.y = y
        self.m = m
        self.radius = radius
        self.color = color
        self.vy = vy
        self.vx = vx
        self.ax = ax
        self.canvas_id = None

    def update(self, WIDTH, HEIGHT, g=0.5):
        if self.vy != 0 or self.y + self.radius < HEIGHT - 1:
            self.vy += g
            
        self.vx += self.ax
        self.x += self.vx
        self.y += self.vy

        # Bottom collision
        if self.y + self.radius >= HEIGHT:
            self.y = HEIGHT - self.radius
            self.vy *= -0.9
            self.vx *= 0.98
            # Stop bouncing if it's too small AND on the ground
            if abs(self.vy) < 1:
                self.vy = 0
            if abs(self.vx) < 0.1:
                self.vx = 0

        # Top collision
        elif self.y - self.radius <= 0:
            self.y = self.radius
            self.vy *= -0.9
            
        # Left wall
        if self.x - self.radius <= 0:
            self.x = self.radius
            self.vx *= -0.9

        # Right wall
        elif self.x + self.radius >= WIDTH:
            self.x = WIDTH - self.radius
            self.vx *= -0.9

    def draw(self, canvas):
        x1 = self.x - self.radius
        y1 = self.y - self.radius
        x2 = self.x + self.radius
        y2 = self.y + self.radius
        
        if self.canvas_id is None:
            self.canvas_id = canvas.create_oval(x1, y1, x2, y2, fill=self.color, outline="black")
        else:
            canvas.coords(self.canvas_id, x1, y1, x2, y2)


def elastic_collision(m1, m2, vx1, vx2, vy1, vy2):
    v1xfinal = ((m1-m2)*vx1 + 2*m2*vx2) / (m1+m2)
    v2xfinal = ((m2-m1)*vx2 + 2*m1*vx1) / (m1+m2)
    v1yfinal = ((m1-m2)*vy1 + 2*m2*vy2) / (m1+m2)
    v2yfinal = ((m2-m1)*vy2 + 2*m1*vy1) / (m1+m2)
    return v1xfinal, v2xfinal, v1yfinal, v2yfinal


def get_distance(ball1, ball2):
    return math.hypot(ball2.x - ball1.x, ball2.y - ball1.y)


class PhysicsSimulation:
    def __init__(self, canvas, ball_amount, masses, vxs, vys):
        self.canvas = canvas
        self.ball_amount = ball_amount
        self.masses = masses
        self.vxs = vxs
        self.vys = vys
        
        self.balls = []
        self.running = False
        self.job_id = None
        
        self.setup()

    def setup(self):
        self.canvas.delete("all")
        self.balls.clear()
        
        # Wait for canvas to draw so we get real width/height
        self.canvas.update_idletasks()
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        # Fallback if canvas hasn't rendered yet
        if width <= 1: width = 800
        if height <= 1: height = 600

        colors = ["red", "blue", "green", "orange", "purple"]

        for i in range(self.ball_amount):
            x_pos = width - (i+1) * 100
            if x_pos < 50: x_pos = 50 + i * 50
            
            radius = max(5, min(5 * self.masses[i], 50)) # Cap radius for sanity
            color = colors[i % len(colors)]
            
            ball = Ball(x_pos, height//2, self.masses[i], radius, color, self.vys[i], self.vxs[i])
            ball.draw(self.canvas)
            self.balls.append(ball)

    def start(self):
        self.running = True
        self.step()

    def stop(self):
        self.running = False
        if self.job_id:
            self.canvas.after_cancel(self.job_id)
            self.job_id = None

    def step(self):
        if not self.running:
            return

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        for ball in self.balls:
            ball.update(width, height)

        # Check collisions
        for i in range(len(self.balls)-1):
            for j in range(i+1, len(self.balls)):
                b1 = self.balls[i]
                b2 = self.balls[j]
                if get_distance(b1, b2) < b1.radius + b2.radius:
                    b1.vx, b2.vx, b1.vy, b2.vy = elastic_collision(
                        b1.m, b2.m, b1.vx, b2.vx, b1.vy, b2.vy
                    )
                    
                    # Prevent sticking by slightly separating them
                    dist = get_distance(b1, b2)
                    overlap = (b1.radius + b2.radius) - dist
                    if overlap > 0 and dist > 0:
                        nx = (b2.x - b1.x) / dist
                        ny = (b2.y - b1.y) / dist
                        b1.x -= nx * overlap / 2
                        b1.y -= ny * overlap / 2
                        b2.x += nx * overlap / 2
                        b2.y += ny * overlap / 2

        for ball in self.balls:
            ball.draw(self.canvas)

        # ~60 FPS
        self.job_id = self.canvas.after(16, self.step)