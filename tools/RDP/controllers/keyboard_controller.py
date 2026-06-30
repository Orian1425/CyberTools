from pynput import keyboard


class KeyboardController:
    def __init__(self):
        self.controller = keyboard.Controller()

    def press(self, key: keyboard.Key):
        self.controller.press(key)

    def release(self, key: keyboard.Key):
        self.controller.release(key)

    def type(self, text: str):
        self.controller.type(text)
