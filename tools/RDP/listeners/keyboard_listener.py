import os
import queue
from pynput import keyboard


class KeyboardListener:
    def __init__(self, q: queue.Queue, shutdown_callback=None):
        self.q = q
        self.ctrl_pressed = False
        self.shutdown_callback = shutdown_callback
        self.listner = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release
        )
    def is_ctrl_pressed(self):
        return self.ctrl_pressed
        
    def on_press(self, key, injected=False):
        self.q.put(f"K:P:{key}")

        if key in (keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
            self.ctrl_pressed = True

        # Check if Escape is pressed WHILE Control is being held down
        if key == keyboard.Key.esc and self.ctrl_pressed:
            if self.shutdown_callback:
                self.shutdown_callback()
            else:
                os._exit(0)

    def on_release(self, key, injected=False):
        self.q.put(f"K:R:{key}")

        if key in (keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
            self.ctrl_pressed = False

    def start_listening(self):
        self.listner.start()
