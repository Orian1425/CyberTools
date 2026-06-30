import queue
from pynput import mouse


class MouseListener:
    def __init__(self, q: queue.Queue):
        self.q = q
        self.listener = mouse.Listener(
            on_move=self.on_move,
            on_click=self.on_click,
            on_scroll=self.on_scroll
        )

    def on_move(self, x, y, injected=False):
        self.q.put(f"M:{x}:{y}")

    def on_click(self, x, y, button, pressed, injected=False):
        self.q.put(f"C:{'P' if pressed else 'R'}:{button}:{x}:{y}")

    def on_scroll(self, x, y, dx, dy, injected=False):
        self.q.put(f"S:{dy}:{dx}")

    def start_listening(self):
        self.listener.start()
