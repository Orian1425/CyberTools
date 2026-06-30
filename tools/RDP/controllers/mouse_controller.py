from pynput import mouse


class MouseController:
    def __init__(self):
        self.controller = mouse.Controller()

    def set_position(self, x, y):
        self.controller.position = (x, y)

    def press(self, button: mouse.Button):
        self.controller.press(button=button)

    def release(self, button: mouse.Button):
        self.controller.release(button=button)

    def scroll(self, dy: int, dx: int):
        self.controller.scroll(dx, dy)
